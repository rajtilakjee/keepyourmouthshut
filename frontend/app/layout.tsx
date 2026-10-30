import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "KeepYourMouthShut",
  description: "Acid Reflux for your Ears!",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
