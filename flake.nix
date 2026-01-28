{
  description = "Statespace development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            cairo
            pkg-config
            libiconv
          ];

          shellHook = ''
            export DYLD_FALLBACK_LIBRARY_PATH="${pkgs.cairo}/lib:${pkgs.libiconv}/lib"
            export LIBRARY_PATH="${pkgs.libiconv}/lib''${LIBRARY_PATH:+:$LIBRARY_PATH}"
            
            # Preserve proxy settings from parent shell
            export HTTP_PROXY="''${HTTP_PROXY:-}"
            export HTTPS_PROXY="''${HTTPS_PROXY:-}"
            export NO_PROXY="''${NO_PROXY:-}"
            export http_proxy="''${http_proxy:-}"
            export https_proxy="''${https_proxy:-}"
            export no_proxy="''${no_proxy:-}"
          '';
        };
      });
}
