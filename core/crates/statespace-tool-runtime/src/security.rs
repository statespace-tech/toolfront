//! SSRF protection for the curl tool.
//!
//! Validates URLs and blocks requests to private/internal networks.

use crate::error::Error;
use std::net::{IpAddr, Ipv4Addr, Ipv6Addr};

pub fn validate_url_initial(url: &str) -> Result<reqwest::Url, Error> {
    let parsed =
        reqwest::Url::parse(url).map_err(|e| Error::InvalidCommand(format!("Invalid URL: {e}")))?;

    if parsed.scheme() != "http" && parsed.scheme() != "https" {
        return Err(Error::Security(format!(
            "Only http/https schemes allowed, got: {}",
            parsed.scheme()
        )));
    }

    let host = parsed
        .host_str()
        .ok_or_else(|| Error::InvalidCommand("URL must have a host".into()))?;

    if is_localhost_name(host) {
        return Err(Error::Security(format!(
            "Access to localhost is not allowed: {host}"
        )));
    }

    if is_metadata_service(host) {
        return Err(Error::Security(format!(
            "Access to metadata service blocked: {host}"
        )));
    }

    if let Ok(ip) = host.parse::<IpAddr>()
        && is_private_or_restricted_ip(&ip)
    {
        return Err(Error::Security(format!(
            "Access to private/restricted IP blocked: {ip}"
        )));
    }

    Ok(parsed)
}

fn is_localhost_name(host: &str) -> bool {
    matches!(
        host.to_lowercase().as_str(),
        "localhost" | "localhost.localdomain"
    )
}

fn is_metadata_service(host: &str) -> bool {
    host == "169.254.169.254" || host == "metadata.google.internal"
}

#[must_use]
pub fn is_private_or_restricted_ip(ip: &IpAddr) -> bool {
    match ip {
        IpAddr::V4(ipv4) => is_private_ipv4(ipv4),
        IpAddr::V6(ipv6) => is_private_ipv6(ipv6),
    }
}

const fn is_private_ipv4(ip: &Ipv4Addr) -> bool {
    ip.is_private()
        || ip.is_loopback()
        || ip.is_link_local()
        || ip.is_broadcast()
        || ip.is_documentation()
        || ip.is_unspecified()
}

fn is_private_ipv6(ip: &Ipv6Addr) -> bool {
    if is_fly_6pn(ip) {
        return false;
    }

    ip.is_loopback()
        || ip.is_unspecified()
        || ip.is_unique_local()
        || ip.is_unicast_link_local()
        || ip.is_multicast()
        || is_ipv6_site_local(ip)
        || is_ipv4_mapped_private(ip)
}

const fn is_fly_6pn(ip: &Ipv6Addr) -> bool {
    ip.segments()[0] == 0xfdaa
}

fn is_ipv6_site_local(ip: &Ipv6Addr) -> bool {
    let s0 = ip.segments()[0];
    (0xfec0..=0xfeff).contains(&s0)
}

const fn is_ipv4_mapped_private(ip: &Ipv6Addr) -> bool {
    if let Some(mapped) = ip.to_ipv4_mapped() {
        is_private_ipv4(&mapped)
    } else {
        false
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_validate_url_allows_https() {
        assert!(validate_url_initial("https://example.com").is_ok());
        assert!(validate_url_initial("https://api.github.com/repos").is_ok());
    }

    #[test]
    fn test_validate_url_allows_http() {
        assert!(validate_url_initial("http://example.com").is_ok());
    }

    #[test]
    fn test_validate_url_blocks_ftp() {
        let result = validate_url_initial("ftp://example.com");
        assert!(matches!(result, Err(Error::Security(_))));
    }

    #[test]
    fn test_validate_url_blocks_file() {
        let result = validate_url_initial("file:///etc/passwd");
        assert!(matches!(result, Err(Error::Security(_))));
    }

    #[test]
    fn test_validate_url_blocks_localhost() {
        assert!(matches!(
            validate_url_initial("http://localhost"),
            Err(Error::Security(_))
        ));
        assert!(matches!(
            validate_url_initial("https://localhost:8080"),
            Err(Error::Security(_))
        ));
    }

    #[test]
    fn test_validate_url_blocks_metadata_service() {
        assert!(matches!(
            validate_url_initial("http://169.254.169.254"),
            Err(Error::Security(_))
        ));
        assert!(matches!(
            validate_url_initial("http://metadata.google.internal"),
            Err(Error::Security(_))
        ));
    }

    #[test]
    fn test_ipv4_blocks_private() {
        assert!(is_private_ipv4(&"10.0.0.1".parse().unwrap()));
        assert!(is_private_ipv4(&"172.16.0.1".parse().unwrap()));
        assert!(is_private_ipv4(&"192.168.1.1".parse().unwrap()));
        assert!(is_private_ipv4(&"127.0.0.1".parse().unwrap()));
    }

    #[test]
    fn test_ipv4_allows_public() {
        assert!(!is_private_ipv4(&"1.1.1.1".parse().unwrap()));
        assert!(!is_private_ipv4(&"8.8.8.8".parse().unwrap()));
    }

    #[test]
    fn test_ipv6_allows_fly_6pn() {
        assert!(!is_private_ipv6(&"fdaa::1".parse().unwrap()));
        assert!(!is_private_ipv6(&"fdaa:0:18:a7b::1".parse().unwrap()));
    }

    #[test]
    fn test_ipv6_blocks_loopback() {
        assert!(is_private_ipv6(&"::1".parse().unwrap()));
    }

    #[test]
    fn test_ipv6_blocks_unique_local() {
        assert!(is_private_ipv6(&"fc00::1".parse().unwrap()));
        assert!(is_private_ipv6(&"fd00::1".parse().unwrap()));
    }
}
