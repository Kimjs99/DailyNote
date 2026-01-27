import { getCollection, type CollectionEntry } from "astro:content";

export async function getBlogPosts() {
  const posts = await getCollection("blog");
  return posts
    .filter((post) => !post.data.draft)
    .sort((a, b) => b.data.pubDate.getTime() - a.data.pubDate.getTime());
}

export function estimateReadingTime(body: string) {
  const words = body.trim().split(/\s+/).length;
  const minutes = Math.max(1, Math.round(words / 200));
  return `${minutes}분 읽기`;
}

export function groupByCategory(posts: CollectionEntry<"blog">[]) {
  const categories = new Map<string, CollectionEntry<"blog">[]>();
  for (const post of posts) {
    const list = categories.get(post.data.category) ?? [];
    list.push(post);
    categories.set(post.data.category, list);
  }
  return [...categories.entries()].sort((a, b) =>
    a[0].localeCompare(b[0])
  );
}

export function groupByTag(posts: CollectionEntry<"blog">[]) {
  const tags = new Map<string, CollectionEntry<"blog">[]>();
  for (const post of posts) {
    for (const tag of post.data.tags) {
      const list = tags.get(tag) ?? [];
      list.push(post);
      tags.set(tag, list);
    }
  }
  return [...tags.entries()].sort((a, b) => a[0].localeCompare(b[0]));
}

export function formatMonthKey(date: Date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  return `${year}-${month}`;
}

export function formatMonth(date: Date) {
  return new Intl.DateTimeFormat("ko-KR", {
    year: "numeric",
    month: "long",
  }).format(date);
}

export function groupByMonth(posts: CollectionEntry<"blog">[]) {
  const months = new Map<
    string,
    { label: string; items: CollectionEntry<"blog">[] }
  >();

  for (const post of posts) {
    const key = formatMonthKey(post.data.pubDate);
    const entry = months.get(key) ?? {
      label: formatMonth(post.data.pubDate),
      items: [],
    };
    entry.items.push(post);
    months.set(key, entry);
  }

  return [...months.entries()]
    .sort((a, b) => b[0].localeCompare(a[0]))
    .map(([key, value]) => ({
      key,
      label: value.label,
      items: value.items,
    }));
}

export function formatDate(date: Date) {
  return new Intl.DateTimeFormat("ko-KR", {
    year: "numeric",
    month: "short",
    day: "2-digit",
  }).format(date);
}

export function slugify(value: string) {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s-]/gu, "")
    .replace(/\s+/g, "-");
}
