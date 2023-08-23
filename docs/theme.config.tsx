import React from "react";
import { useRouter } from "next/router";
import { DocsThemeConfig, useConfig } from "nextra-theme-docs";

import Logo from "components/logo";
import Head from "components/head";
import Footer from "components/footer";

const config: DocsThemeConfig = {
  banner: {
    dismissible: false,
    key: "under-active-development",
    text: <p>Under Active Development</p>,
  },

  logo: <Logo />,
  logoLink: "/",

  project: {
    link: "https://github.com/stepbrobd/metaprocessor",
  },
  docsRepositoryBase:
    "https://github.com/stepbrobd/metaprocessor/tree/master/docs",

  sidebar: {
    autoCollapse: true,
    toggleButton: true,
    defaultMenuCollapseLevel: 999,
  },

  toc: {
    float: true,
  },

  useNextSeoProps() {
    const { asPath } = useRouter();
    if (asPath !== "/") {
      return {
        titleTemplate: "%s – MetaProcessor",
      };
    }
  },

  head: () => {
    const { asPath, defaultLocale, locale } = useRouter();
    const { frontMatter } = useConfig();
    const url =
      "https://metaprocessor.org" +
      (defaultLocale === locale ? asPath : `/${locale}${asPath}`);

    return (
      <Head
        url={url}
        title={frontMatter.title}
        description={frontMatter.description}
      />
    );
  },

  footer: {
    text: <Footer />,
  },
};

export default config;
