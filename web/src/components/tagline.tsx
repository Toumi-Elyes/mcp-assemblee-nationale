"use client";

import { useEffect, useRef } from "react";

const TAGLINE = "Les chiffres viennent de l'Assemblée. Les liens mènent à la source. Le jugement vous appartient.";
const TRIGGER_MARGIN = "0px 0px -40% 0px";
const WORD_STEP_MS = 60;
const WORD_CAP_MS = 400;

export const Tagline: React.FC = () => {
  const container = useRef<HTMLParagraphElement>(null);
  const words = TAGLINE.split(" ");

  useEffect(() => {
    const root = container.current;
    if (root === null) {
      return;
    }
    const elements = Array.from(root.querySelectorAll<HTMLElement>(".word"));
    const observer = new IntersectionObserver(
      (entries) => {
        const crossing = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => Number((a.target as HTMLElement).dataset.index) - Number((b.target as HTMLElement).dataset.index));
        crossing.forEach((entry, order) => {
          const target = entry.target as HTMLElement;
          target.style.transitionDelay = `${Math.min(order * WORD_STEP_MS, WORD_CAP_MS)}ms`;
          target.setAttribute("data-on", "");
          observer.unobserve(target);
        });
      },
      { rootMargin: TRIGGER_MARGIN },
    );
    for (const element of elements) {
      observer.observe(element);
    }
    return () => {
      observer.disconnect();
    };
  }, []);

  return (
    <section aria-label="Notre principe" className="py-24 sm:py-24">
      <div className="mx-auto w-full max-w-page px-4 sm:px-6">
        <p ref={container} className="max-w-hero text-4xl font-semibold tracking-tight sm:text-5xl">
          <span className="sr-only">{TAGLINE}</span>
          <span aria-hidden="true">
            {words.map((word, index) => (
              <span key={`${word}-${index}`} data-index={index} className="word">
                {word}{" "}
              </span>
            ))}
          </span>
        </p>
      </div>
    </section>
  );
};
