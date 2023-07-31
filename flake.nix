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
        lib = pkgs.lib;
        stdenv = pkgs.stdenv;

        python3 = pkgs.python3;
        withPackages = python3.withPackages;
        buildPythonPackage = python3.pkgs.buildPythonPackage;
        pythonOlder = python3.pkgs.pythonOlder;

        pythonDevEnv = withPackages (ps: with ps; [
          pip
          setuptools
          wheel
        ]);

        pythonBuildEnv = withPackages (ps: with ps; [
          boto3
          click
          click-aliases
          click-option-group
          numpy
          pandas
          pyarrow
          rich
          toml
          tqdm
        ] ++ lib.optionals stdenv.isLinux (with ps; [
          metawear
        ]));

        metaprocessor = buildPythonPackage rec {
          pname = "metaprocessor";
          inherit ((lib.importTOML ./pyproject.toml).project) version;
          format = "pyproject";
          disabled = pythonOlder "3";

          enableParallelBuilding = true;

          src = lib.cleanSource ./.;

          propagatedBuildInputs = [ pythonBuildEnv ];
        };
      in
      {
        packages.default = metaprocessor;

        overlays.default = _: prev: {
          metaprocessor = prev.metaprocessor.override { };
        };

        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            pythonDevEnv
            pythonBuildEnv
            ruff
          ];
        };

        formatter = pkgs.nixpkgs-fmt;
      }
    );
}
