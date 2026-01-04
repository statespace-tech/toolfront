//! Tool domain models

use crate::error::Error;
use serde::{Deserialize, Serialize};
use std::fmt;
use std::str::FromStr;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, Deserialize, Serialize)]
#[serde(rename_all = "UPPERCASE")]
#[non_exhaustive]
pub enum HttpMethod {
    #[default]
    Get,
    Post,
    Put,
    Patch,
    Delete,
    Head,
    Options,
}

impl HttpMethod {
    #[must_use]
    pub const fn as_str(&self) -> &'static str {
        match self {
            Self::Get => "GET",
            Self::Post => "POST",
            Self::Put => "PUT",
            Self::Patch => "PATCH",
            Self::Delete => "DELETE",
            Self::Head => "HEAD",
            Self::Options => "OPTIONS",
        }
    }
}

impl fmt::Display for HttpMethod {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

impl FromStr for HttpMethod {
    type Err = Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_uppercase().as_str() {
            "GET" => Ok(Self::Get),
            "POST" => Ok(Self::Post),
            "PUT" => Ok(Self::Put),
            "PATCH" => Ok(Self::Patch),
            "DELETE" => Ok(Self::Delete),
            "HEAD" => Ok(Self::Head),
            "OPTIONS" => Ok(Self::Options),
            _ => Err(Error::InvalidCommand(format!("Unknown HTTP method: {s}"))),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize, Serialize)]
#[serde(tag = "type", rename_all = "lowercase")]
#[non_exhaustive]
pub enum BuiltinTool {
    Glob { pattern: String },
    Curl { url: String, method: HttpMethod },
    Exec { command: String, args: Vec<String> },
}

impl BuiltinTool {
    pub fn from_command(command: &[String]) -> Result<Self, Error> {
        if command.is_empty() {
            return Err(Error::InvalidCommand("Command cannot be empty".to_string()));
        }

        const ALLOWED_COMMANDS: &[&str] = &[
            "grep",
            "head",
            "tail",
            "wc",
            "sort",
            "uniq",
            "cut",
            "sed",
            "awk",
            "find",
            "tree",
            "file",
            "stat",
            "md5sum",
            "sha256sum",
            "du",
        ];

        match command[0].as_str() {
            "ls" => Ok(Self::Exec {
                command: "ls".to_string(),
                args: command[1..].to_vec(),
            }),
            "cat" => {
                if command.len() < 2 {
                    return Err(Error::InvalidCommand(
                        "cat requires a path argument".to_string(),
                    ));
                }
                Ok(Self::Exec {
                    command: "cat".to_string(),
                    args: command[1..].to_vec(),
                })
            }
            "glob" => {
                if command.len() < 2 {
                    return Err(Error::InvalidCommand(
                        "glob requires a pattern argument".to_string(),
                    ));
                }
                Ok(Self::Glob {
                    pattern: command[1].clone(),
                })
            }
            "curl" => Self::parse_curl(&command[1..]),
            cmd if ALLOWED_COMMANDS.contains(&cmd) => Ok(Self::Exec {
                command: cmd.to_string(),
                args: command[1..].to_vec(),
            }),
            _ => Err(Error::InvalidCommand(format!(
                "Unknown or disallowed tool: {}",
                command[0]
            ))),
        }
    }

    fn parse_curl(args: &[String]) -> Result<Self, Error> {
        #[derive(Debug)]
        struct CurlArgs {
            url: Option<String>,
            method: Option<String>,
        }

        let parsed = args.iter().try_fold(
            (
                CurlArgs {
                    url: None,
                    method: None,
                },
                None::<&str>,
            ),
            |(mut acc, expecting_value), arg| match expecting_value {
                Some("-X" | "--request") => {
                    acc.method = Some(arg.clone());
                    Ok((acc, None))
                }
                Some(flag) => Err(Error::InvalidCommand(format!("Unknown flag: {flag}"))),
                None if arg == "-X" || arg == "--request" => Ok((acc, Some(arg.as_str()))),
                None if !arg.starts_with('-') && acc.url.is_none() => {
                    acc.url = Some(arg.clone());
                    Ok((acc, None))
                }
                None if arg.starts_with('-') => {
                    Err(Error::InvalidCommand(format!("Unknown flag: {arg}")))
                }
                None => Ok((acc, None)),
            },
        );

        let (args, expecting) = parsed?;

        if let Some(flag) = expecting {
            return Err(Error::InvalidCommand(format!(
                "{flag} requires a method argument"
            )));
        }

        let url = args
            .url
            .ok_or_else(|| Error::InvalidCommand("curl requires a URL argument".to_string()))?;

        let method = match args.method {
            Some(m) => m.parse()?,
            None => HttpMethod::default(),
        };

        Ok(Self::Curl { url, method })
    }

    #[must_use]
    pub const fn name(&self) -> &'static str {
        match self {
            Self::Glob { .. } => "glob",
            Self::Curl { .. } => "curl",
            Self::Exec { .. } => "exec",
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_builtin_tool_name() {
        let exec = BuiltinTool::Exec {
            command: "ls".to_string(),
            args: vec![],
        };
        assert_eq!(exec.name(), "exec");
    }

    #[test]
    fn test_from_command_ls() {
        let tool = BuiltinTool::from_command(&["ls".to_string(), "docs/".to_string()]).unwrap();
        assert!(matches!(
            tool,
            BuiltinTool::Exec { command, args } if command == "ls" && args == vec!["docs/"]
        ));
    }

    #[test]
    fn test_from_command_cat() {
        let tool = BuiltinTool::from_command(&["cat".to_string(), "file.md".to_string()]).unwrap();
        assert!(matches!(
            tool,
            BuiltinTool::Exec { command, args } if command == "cat" && args == vec!["file.md"]
        ));

        let result = BuiltinTool::from_command(&["cat".to_string()]);
        assert!(matches!(result, Err(Error::InvalidCommand(_))));
    }

    #[test]
    fn test_from_command_glob() {
        let tool = BuiltinTool::from_command(&["glob".to_string(), "*.md".to_string()]).unwrap();
        assert_eq!(
            tool,
            BuiltinTool::Glob {
                pattern: "*.md".to_string()
            }
        );
    }

    #[test]
    fn test_from_command_curl() {
        let tool =
            BuiltinTool::from_command(&["curl".to_string(), "https://api.github.com".to_string()])
                .unwrap();
        assert_eq!(
            tool,
            BuiltinTool::Curl {
                url: "https://api.github.com".to_string(),
                method: HttpMethod::Get,
            }
        );

        let tool = BuiltinTool::from_command(&[
            "curl".to_string(),
            "-X".to_string(),
            "POST".to_string(),
            "https://api.github.com".to_string(),
        ])
        .unwrap();
        assert_eq!(
            tool,
            BuiltinTool::Curl {
                url: "https://api.github.com".to_string(),
                method: HttpMethod::Post,
            }
        );
    }

    #[test]
    fn test_from_command_unknown() {
        let result = BuiltinTool::from_command(&["unknown".to_string()]);
        assert!(matches!(result, Err(Error::InvalidCommand(_))));
    }

    #[test]
    fn test_http_method_parsing() {
        assert_eq!("GET".parse::<HttpMethod>().unwrap(), HttpMethod::Get);
        assert_eq!("post".parse::<HttpMethod>().unwrap(), HttpMethod::Post);
        assert!("INVALID".parse::<HttpMethod>().is_err());
    }
}
