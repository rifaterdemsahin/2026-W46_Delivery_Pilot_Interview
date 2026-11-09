import { AbsoluteFill, Img, staticFile } from "remotion";

// public/thumb_frame.jpg is extracted from the 4K source by scripts/10_make_thumbnail.sh (git-ignored)
const RED = "#ff2b2b";
const outline = { WebkitTextStroke: "10px #000", paintOrder: "stroke fill" } as const;
const big = { fontFamily: "Impact, 'Arial Black', Helvetica, sans-serif", textTransform: "uppercase", lineHeight: 0.95, ...outline } as const;

/** 1280x720 YouTube thumbnail: one real frame + a big three-word headline. Text is drawn here, never by an image model. */
export const Thumbnail = () => (
  <AbsoluteFill style={{ background: "black" }}>
    <AbsoluteFill style={{ transform: "scale(1.08)", transformOrigin: "75% 45%" }}>
      <Img src={staticFile("thumb_frame.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
    </AbsoluteFill>
    {/* darken the left for legibility */}
    <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(0,0,0,0.78) 0%, rgba(0,0,0,0.45) 42%, rgba(0,0,0,0) 62%)" }} />
    <AbsoluteFill style={{ padding: "52px 0 0 56px", justifyContent: "flex-start", alignItems: "flex-start" }}>
      <div style={{ ...big, fontSize: 118, color: "white" }}>Become a</div>
      <div style={{ ...big, fontSize: 118, color: "white" }}>Delivery</div>
      <div style={{ ...big, fontSize: 190, color: RED, marginTop: 4 }}>Pilot</div>
      <div style={{ marginTop: 22, background: RED, color: "white", fontFamily: "Helvetica, Arial, sans-serif", fontWeight: 800, fontSize: 38, padding: "8px 20px", borderRadius: 6, transform: "rotate(-1.5deg)" }}>
        AI builds the bots. You fly them.
      </div>
    </AbsoluteFill>
    <div style={{ position: "absolute", right: 36, bottom: 30, fontFamily: "Helvetica, Arial, sans-serif", fontWeight: 800, fontSize: 30, color: "white", background: "rgba(0,0,0,0.65)", padding: "6px 16px", borderRadius: 6 }}>
      Rifat Erdem Sahin
    </div>
  </AbsoluteFill>
);
