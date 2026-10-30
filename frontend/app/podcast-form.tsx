"use client";

import Image from "next/image";
import { FormEvent, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

const TABS = [
  { id: "description", label: "Description" },
  { id: "topics", label: "Topics" },
  { id: "adverts", label: "Adverts" },
] as const;

type TabId = (typeof TABS)[number]["id"];

type Fields = {
  name: string;
  desc: string;
  topic1: string;
  topic2: string;
  topic3: string;
  advert1: string;
  advert2: string;
};

const EMPTY_FIELDS: Fields = {
  name: "",
  desc: "",
  topic1: "",
  topic2: "",
  topic3: "",
  advert1: "",
  advert2: "",
};

const TAB_FIELDS: Record<TabId, (keyof Fields)[]> = {
  description: ["name", "desc"],
  topics: ["topic1", "topic2", "topic3"],
  adverts: ["advert1", "advert2"],
};

async function readError(response: Response): Promise<string> {
  const payload = (await response.json().catch(() => null)) as {
    detail?: unknown;
  } | null;
  if (typeof payload?.detail === "string") {
    return payload.detail;
  }
  if (response.status === 422) {
    return "Fill in every field before generating.";
  }
  return "Podcast generation failed.";
}

export function PodcastForm() {
  const [tab, setTab] = useState<TabId>("description");
  const [fields, setFields] = useState<Fields>(EMPTY_FIELDS);
  const [pending, setPending] = useState(false);
  const [message, setMessage] = useState("");
  const [failed, setFailed] = useState(false);

  function update(key: keyof Fields, value: string) {
    setFields((current) => ({ ...current, [key]: value }));
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const missingTab = TABS.find((item) =>
      TAB_FIELDS[item.id].some((key) => fields[key].trim() === ""),
    );
    if (missingTab) {
      setTab(missingTab.id);
      setFailed(true);
      setMessage("Fill in every field before generating.");
      return;
    }

    setPending(true);
    setFailed(false);
    setMessage("Generating the podcast. This can take a few minutes.");

    try {
      const response = await fetch(`${API_URL}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(fields),
      });
      if (!response.ok) {
        throw new Error(await readError(response));
      }

      const blob = await response.blob();
      const filename =
        /filename="?([^"]+)"?/.exec(
          response.headers.get("Content-Disposition") ?? "",
        )?.[1] ?? "podcast.zip";
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      link.click();
      URL.revokeObjectURL(url);
      setFailed(false);
      setMessage("Your podcast download has started.");
    } catch (error) {
      setFailed(true);
      setMessage(error instanceof Error ? error.message : "Podcast generation failed.");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="page">
      <div className="container">
        <div className="brand">
          <Image
            src="/kyms-logo.png"
            alt="KeepYourMouthShut logo"
            width={130}
            height={130}
            className="logo"
            priority
          />
          <h1>KeepYourMouthShut</h1>
          <h3>Acid Reflux for your Ears!</h3>
          <a
            className="sponsor"
            href="https://github.com/sponsors/rajtilakjee"
            target="_blank"
            rel="noreferrer"
          >
            🧡 Sponsor
          </a>
        </div>

        <div className="tabs" role="tablist">
          {TABS.map((item) => (
            <button
              key={item.id}
              type="button"
              role="tab"
              aria-selected={tab === item.id}
              className={tab === item.id ? "active" : undefined}
              onClick={() => setTab(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>

        <form noValidate onSubmit={onSubmit}>
          <div id="description" className={tab === "description" ? "tab active" : "tab"} role="tabpanel">
            <label htmlFor="name">Podcast Name:</label>
            <textarea
              id="name"
              name="name"
              value={fields.name}
              required
              onChange={(event) => update("name", event.target.value)}
            />
            <label htmlFor="desc">Podcast Description:</label>
            <textarea
              id="desc"
              name="desc"
              value={fields.desc}
              required
              onChange={(event) => update("desc", event.target.value)}
            />
          </div>

          <div id="topics" className={tab === "topics" ? "tab active" : "tab"} role="tabpanel">
            <label htmlFor="topic1">Topic 1:</label>
            <textarea
              id="topic1"
              name="topic1"
              value={fields.topic1}
              required
              onChange={(event) => update("topic1", event.target.value)}
            />
            <label htmlFor="topic2">Topic 2:</label>
            <textarea
              id="topic2"
              name="topic2"
              value={fields.topic2}
              required
              onChange={(event) => update("topic2", event.target.value)}
            />
            <label htmlFor="topic3">Topic 3:</label>
            <textarea
              id="topic3"
              name="topic3"
              value={fields.topic3}
              required
              onChange={(event) => update("topic3", event.target.value)}
            />
          </div>

          <div id="adverts" className={tab === "adverts" ? "tab active" : "tab"} role="tabpanel">
            <label htmlFor="advert1">Advert 1:</label>
            <textarea
              id="advert1"
              name="advert1"
              value={fields.advert1}
              required
              onChange={(event) => update("advert1", event.target.value)}
            />
            <label htmlFor="advert2">Advert 2:</label>
            <textarea
              id="advert2"
              name="advert2"
              value={fields.advert2}
              required
              onChange={(event) => update("advert2", event.target.value)}
            />
          </div>

          <button className="submit" type="submit" disabled={pending}>
            {pending ? "Generating..." : "Generate Podcast"}
          </button>
          {message ? <p className={failed ? "status error" : "status"}>{message}</p> : null}
        </form>
      </div>
    </div>
  );
}
