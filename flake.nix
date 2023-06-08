{
  inputs = {
    nixpkgs.url = "flake:nixpkgs/nixpkgs-unstable";
    utils.url = "flake:flake-utils";
  };

  outputs = { self, nixpkgs, utils, ... }: utils.lib.eachSystem [
    "aarch64-darwin"
    "x86_64-darwin"
    "aarch64-linux"
    "x86_64-linux"
  ]
    (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          setuptools
        ]);

        metaprocessor = pkgs.python3.pkgs.buildPythonPackage rec {
          format = "pyproject";

          pname = "metaprocessor";
          inherit ((pkgs.lib.importTOML ./pyproject.toml).project) version;

          src = pkgs.lib.cleanSource ./.;

          propagatedBuildInputs = [
            pythonEnv
          ];
        };
      in
      {
        packages.default = metaprocessor;

        overlays.default = _: prev: {
          metaprocessor = prev.metaprocessor.override { };
        };

        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            pythonEnv
            ruff
            openssl
          ];
        };

        formatter = pkgs.nixpkgs-fmt;
      }
    );
}
