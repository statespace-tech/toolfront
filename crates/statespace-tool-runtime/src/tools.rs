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
    /// # Errors
    ///
    /// Returns an error when the command is empty or malformed.
    pub fn from_command(command: &[String]) -> Result<Self, Error> {
        if command.is_empty() {
            return Err(Error::InvalidCommand("Command cannot be empty".to_string()));
        }

        match command[0].as_str() {
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
            cmd => Ok(Self::Exec {
                command: cmd.to_string(),
                args: command[1..].to_vec(),
            }),
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

    pub const fn requires_egress(&self) -> bool {
        matches!(self, Self::Curl { .. })
    }

    pub fn is_free_tier_allowed(&self) -> bool {
        match self {
            Self::Glob { .. } => true,
            Self::Curl { .. } => false,
            Self::Exec { command, .. } => FREE_TIER_COMMAND_ALLOWLIST.contains(&command.as_str()),
        }
    }
}

pub const FREE_TIER_COMMAND_ALLOWLIST: &[&str] = &[
    "cat",
    "head",
    "tail",
    "less",
    "more",
    "wc",
    "sort",
    "uniq",
    "cut",
    "paste",
    "tr",
    "tee",
    "split",
    "csplit",
    "ls",
    "stat",
    "file",
    "du",
    "df",
    "find",
    "which",
    "whereis",
    "cp",
    "mv",
    "rm",
    "mkdir",
    "rmdir",
    "touch",
    "ln",
    "grep",
    "egrep",
    "fgrep",
    "sed",
    "awk",
    "diff",
    "comm",
    "cmp",
    "jq",
    "tar",
    "gzip",
    "gunzip",
    "zcat",
    "bzip2",
    "bunzip2",
    "xz",
    "unxz",
    "echo",
    "printf",
    "true",
    "false",
    "yes",
    "date",
    "cal",
    "env",
    "printenv",
    "basename",
    "dirname",
    "realpath",
    "readlink",
    "pwd",
    "id",
    "whoami",
    "uname",
    "hostname",
    "md5sum",
    "sha256sum",
    "base64",
    "xxd",
    "hexdump",
    "od",
];

#[cfg(test)]
#[allow(clippy::unwrap_used)]
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

        let tool = BuiltinTool::from_command(&["cat".to_string()]).unwrap();
        assert!(matches!(
            tool,
            BuiltinTool::Exec { command, args } if command == "cat" && args.is_empty()
        ));
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
    fn test_from_command_custom() {
        let tool = BuiltinTool::from_command(&["jq".to_string(), ".".to_string()]).unwrap();
        assert!(matches!(
            tool,
            BuiltinTool::Exec { command, args } if command == "jq" && args == vec!["."]
        ));

        let tool =
            BuiltinTool::from_command(&["node".to_string(), "script.js".to_string()]).unwrap();
        assert!(matches!(
            tool,
            BuiltinTool::Exec { command, args } if command == "node" && args == vec!["script.js"]
        ));
    }

    #[test]
    fn test_http_method_parsing() {
        assert_eq!("GET".parse::<HttpMethod>().unwrap(), HttpMethod::Get);
        assert_eq!("post".parse::<HttpMethod>().unwrap(), HttpMethod::Post);
        assert!("INVALID".parse::<HttpMethod>().is_err());
    }

    #[test]
    fn test_is_free_tier_allowed_glob() {
        let tool = BuiltinTool::Glob {
            pattern: "*.md".to_string(),
        };
        assert!(tool.is_free_tier_allowed());
    }

    #[test]
    fn test_is_free_tier_allowed_curl_blocked() {
        let tool = BuiltinTool::Curl {
            url: "https://example.com".to_string(),
            method: HttpMethod::Get,
        };
        assert!(!tool.is_free_tier_allowed());
    }

    #[test]
    fn test_is_free_tier_allowed_allowlisted_commands() {
        for cmd in ["cat", "ls", "grep", "sed", "awk", "jq", "head", "tail"] {
            let tool = BuiltinTool::Exec {
                command: cmd.to_string(),
                args: vec![],
            };
            assert!(tool.is_free_tier_allowed(), "{cmd} should be allowed");
        }
    }

    #[test]
    fn test_is_free_tier_blocked_dangerous_commands() {
        for cmd in [
            "wget", "nc", "ssh", "node", "ruby", "curl", "apt", "pip", "npm",
        ] {
            let tool = BuiltinTool::Exec {
                command: cmd.to_string(),
                args: vec![],
            };
            assert!(!tool.is_free_tier_allowed(), "{cmd} should be blocked");
        }
    }

    #[test]
    fn test_requires_egress() {
        assert!(
            BuiltinTool::Curl {
                url: "https://example.com".to_string(),
                method: HttpMethod::Get,
            }
            .requires_egress()
        );

        assert!(
            !BuiltinTool::Glob {
                pattern: "*.md".to_string(),
            }
            .requires_egress()
        );

        assert!(
            !BuiltinTool::Exec {
                command: "ls".to_string(),
                args: vec![],
            }
            .requires_egress()
        );
    }
}
