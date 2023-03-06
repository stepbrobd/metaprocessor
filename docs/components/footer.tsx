import Logo from "components/logo";

const Footer = () => {
  // vercel detected commit hash or fallback to initial commit hash
  const commit =
    process.env.NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA ||
    "bf64b3f38296fe9b953b3f795be2259fa01571b1";

  return (
    <div className="flex flex-col items-center sm:items-start space-y-6">
      <Logo />
      <small>
        <a
          href={`https://github.com/metaprocessor/metaprocessor/commit/${commit}`}
          target="_blank"
        >
          Commit digest: <u className="font-mono">{commit.substring(0, 17)}</u>.
        </a>
      </small>
      <small>
        Copyright &copy; {new Date().getFullYear()}{" "}
        <a
          href="https://github.com/metaprocessor/metaprocessor/graphs/contributors"
          target="_blank"
        >
          <u>MetaProcessor contributors</u>
        </a>
        .
      </small>
    </div>
  );
};

export default Footer;
