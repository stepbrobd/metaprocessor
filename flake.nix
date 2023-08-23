{
  inputs = {
    nixpkgs.url = "flake:nixpkgs/nixpkgs-unstable";
    utils.url = "flake:flake-utils";
  };

  outputs =
    { self, nixpkgs, utils }: utils.lib.eachDefaultSystem
      (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };
        lib = pkgs.lib;
        stdenv = if pkgs.stdenv.isLinux then pkgs.stdenv else pkgs.clangStdenv;

        ldLibraryPath = with pkgs; lib.makeLibraryPath [
          libffi
          openssl
          stdenv.cc.cc
        ];

        python3 = pkgs.python3;
        python3Env = (python3.withPackages (ps: with ps; [
          pip
          setuptools
          virtualenvwrapper
          wheel

          boto3
          click
          click-aliases
          click-option-group
          numpy
          pandas
          pyarrow
          rich
          scipy
          toml
          tqdm
        ] ++ lib.optionals stdenv.isLinux (with ps; [
          metawear
        ]))).override (args: { ignoreCollisions = true; });

        metaprocessor = python3.pkgs.buildPythonPackage rec {
          pname = "metaprocessor";
          inherit ((lib.importTOML ./pyproject.toml).project) version;

          format = "pyproject";
          disabled = python3.pkgs.pythonOlder "3";

          enableParallelBuilding = true;
          src = lib.cleanSource ./.;
          propagatedBuildInputs = [ python3Env ];
        };
      in
      {
        packages.default = metaprocessor;

        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            direnv
            git
            nix-direnv
            ruff
          ];

          buildInputs = [ python3Env ];

          shellHook = ''
            export "LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${ldLibraryPath}"
            export "SOURCE_DATE_EPOCH=$(date +%s)"
            export "VENV=.venv"

            if [ ! -d "$VENV" ]; then
              virtualenv "$VENV"
            fi

            source "$VENV/bin/activate"
            export "PYTHONPATH=$PWD/$VENV/${python3.sitePackages}/:$PYTHONPATH"
            pip install --editable .
          '';
        };

        formatter = pkgs.nixpkgs-fmt;
      }
      ) // {
      overlays.default = final: prev: {
        inherit (self.packages.${final.system}) metaprocessor;
      };
    };
}
