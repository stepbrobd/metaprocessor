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
          <u className="font-mono">{commit.substring(0, 17)}</u>
        </a>
      </small>
      <small>
        <a href="https://iss.mech.utah.edu" target="_blank">
          <u>ISS Lab</u>
        </a>{" "}
        and{" "}
        <a href="https://batemanhornecenter.org" target="_blank">
          <u>Bateman Horne Center</u>
        </a>
      </small>
      <small>
        &copy; {new Date().getFullYear()}{" "}
        <a
          href="https://github.com/metaprocessor/metaprocessor/graphs/contributors"
          target="_blank"
        >
          <u>MetaProcessor Contributors</u>
        </a>
      </small>
    </div>
  );
};

export default Footer;
