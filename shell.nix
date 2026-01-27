{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    cairo
    pkg-config
    libiconv
  ];

  shellHook = ''
    export DYLD_FALLBACK_LIBRARY_PATH="${pkgs.cairo}/lib"
  '';
}