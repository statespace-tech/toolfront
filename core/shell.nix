{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    rustup
    libiconv
  ];

  LIBRARY_PATH = pkgs.lib.makeLibraryPath (with pkgs; [
    libiconv
  ]);
}
