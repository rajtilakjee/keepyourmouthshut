import { PodcastForm } from "./podcast-form";

export default function Home() {
  return (
    <>
      <PodcastForm />
      <footer className="footer">
        <a href="https://www.keepyourmouthshut.net/" target="_blank" rel="noreferrer">
          Website
        </a>
        <a
          href="https://github.com/rajtilakjee/keepyourmouthshut/blob/main/LICENSE"
          target="_blank"
          rel="noreferrer"
        >
          License
        </a>
        <a href="https://github.com/rajtilakjee/keepyourmouthshut" target="_blank" rel="noreferrer">
          GitHub
        </a>
        <br />
        Copyright &copy; 2023 - Rajtilak Bhattacharjee
        <br />
        Made with ❤️ by Rajtilak Bhattacharjee
      </footer>
    </>
  );
}
