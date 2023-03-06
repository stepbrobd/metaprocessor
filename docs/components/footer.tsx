import Logo from "components/logo";

const Footer = () => {
  return (
    <div className="flex flex-col items-center sm:items-start space-y-4">
      <Logo />
      <small>
        &copy; {new Date().getFullYear()}{" "}
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
