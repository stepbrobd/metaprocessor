import React from "react";
import { useRouter } from "next/router";
import { DocsThemeConfig, useConfig } from "nextra-theme-docs";

const config: DocsThemeConfig = {
  banner: {
    dismissible: false,
    key: "under-active-development",
    text: <p>Under Active Development</p>,
  },

  logo: (
    <span>
      <strong>MetaProcessor</strong>
    </span>
  ),

  project: {
    link: "https://github.com/metaprocessor/metaprocessor",
  },
  docsRepositoryBase: "https://github.com/metaprocessor/metaprocessor/tree/master/docs/pages",

  useNextSeoProps() {
    return {
      titleTemplate: "%s – MetaProcessor",
    };
  },

  head: () => {
    const { asPath, defaultLocale, locale } = useRouter();
    const { frontMatter } = useConfig();
    const url =
      "https://metaprocessor.org" +
      (defaultLocale === locale ? asPath : `/${locale}${asPath}`);

    return (
      <>
        <link
          rel="apple-touch-icon"
          sizes="57x57"
          href="/apple-icon-57x57.png"
        />
        <link
          rel="apple-touch-icon"
          sizes="60x60"
          href="/apple-icon-60x60.png"
        />
        <link
          rel="apple-touch-icon"
          sizes="72x72"
          href="/apple-icon-72x72.png"
        />
        <link
          rel="apple-touch-icon"
          sizes="76x76"
          href="/apple-icon-76x76.png"
        />
        <link
          rel="apple-touch-icon"
          sizes="114x114"
          href="/apple-icon-114x114.png"
        />
        <link
          rel="apple-touch-icon"
          sizes="120x120"
          href="/apple-icon-120x120.png"
        />
        <link
          rel="apple-touch-icon"
          sizes="144x144"
          href="/apple-icon-144x144.png"
        />
        <link
          rel="apple-touch-icon"
          sizes="152x152"
          href="/apple-icon-152x152.png"
        />
        <link
          rel="apple-touch-icon"
          sizes="180x180"
          href="/apple-icon-180x180.png"
        />
        <link
          rel="icon"
          type="image/png"
          sizes="192x192"
          href="/android-icon-192x192.png"
        />
        <link
          rel="icon"
          type="image/png"
          sizes="32x32"
          href="/favicon-32x32.png"
        />
        <link
          rel="icon"
          type="image/png"
          sizes="96x96"
          href="/favicon-96x96.png"
        />
        <link
          rel="icon"
          type="image/png"
          sizes="16x16"
          href="/favicon-16x16.png"
        />
        <meta property="og:url" content={url} />
        <meta
          property="og:title"
          content={frontMatter.title || "MetaProcessor"}
        />
        <meta
          property="og:description"
          content={
            frontMatter.description ||
            "MetaProcessor, all-in-one data pipeline for MbientLab MetaWear series sensors!"
          }
        />
      </>
    );
  },

  footer: {
    text: (
      <span>
        Copyright &copy; {new Date().getFullYear()} MetaProcessor Authors. All Rights Reserved.
      </span>
    ),
  },
};

export default config;
