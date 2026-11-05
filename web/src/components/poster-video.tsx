"use client";

import { useCallback, useSyncExternalStore } from "react";

type PosterVideoProps = React.VideoHTMLAttributes<HTMLVideoElement> & {
  poster: string;
  /** Media query under which this video is the one on screen. */
  media: string;
};

const matchesNever = () => false;

// A browser downloads a <video> poster even when the video is hidden with CSS, so the
// landscape and portrait thumbnails were both fetched. The poster is only set on the
// video that matches the screen; its frame keeps its aspect ratio, so nothing moves.
export const PosterVideo: React.FC<PosterVideoProps> = ({ poster, media, ...props }) => {
  const subscribe = useCallback(
    (onChange: () => void) => {
      const query = window.matchMedia(media);
      query.addEventListener("change", onChange);
      return () => query.removeEventListener("change", onChange);
    },
    [media],
  );
  const isShown = useSyncExternalStore(subscribe, () => window.matchMedia(media).matches, matchesNever);

  return <video {...props} poster={isShown ? poster : undefined} />;
};
