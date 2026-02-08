import { Hero } from "@/components/landing/Hero";
import { Features } from "@/components/landing/Features";
import { CTA } from "@/components/landing/CTA";
import { Footer } from "@/components/landing/Footer";

export const metadata = {
  title: "Todo App - Organize Your Tasks Effortlessly",
  description:
    "Stay productive and focused with a beautiful, intuitive todo app. Manage your tasks with ease and get things done faster.",
};

export default function LandingPage() {
  return (
    <>
      <Hero />
      <Features />
      <CTA />
      <Footer />
    </>
  );
}
