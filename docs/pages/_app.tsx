import "styles/tailwind.css";

import { AppProps } from "next/app";
import Script from "next/script";

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <Component {...pageProps} />
      <Script
        defer
        id="plausible-analytics"
        strategy="afterInteractive"
        data-domain="metaprocessor.org"
        src={"https://plausible.io/js/plausible.js"}
      />
    </>
  );
}
