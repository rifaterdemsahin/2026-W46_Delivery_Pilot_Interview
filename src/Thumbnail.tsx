import { AbsoluteFill, Img, staticFile } from "remotion";

// public/visuals/thumb_bg.jpg   = fal.ai art (scripts/12_generate_thumbnail_art.py), committed
// public/thumb_frame.jpg        = frame from the 4K source (scripts/10_make_thumbnail.sh), git-ignored
const RED = "#ff2b2b";
const stroke = { WebkitTextStroke: "10px #000", paintOrder: "stroke fill" } as const;
const big = { fontFamily: "Impact, 'Arial Black', Helvetica, sans-serif", textTransform: "uppercase", lineHeight: 0.92, ...stroke } as const;

/** 1280x720 curiosity thumbnail: AI art of one pilot facing a wall of bots + a specific hook ("300 bots") + an open question. */
export const Thumbnail = () => (
  <AbsoluteFill style={{ background: "black" }}>
    <Img src={staticFile("visuals/thumb_bg.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "saturate(1.25) contrast(1.1)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(0,0,0,0.88) 0%, rgba(0,0,0,0.62) 45%, rgba(0,0,0,0.1) 75%)" }} />

    <AbsoluteFill style={{ padding: "56px 0 0 56px", justifyContent: "flex-start", alignItems: "flex-start" }}>
      <div style={{ ...big, fontSize: 150, color: "white" }}>300 Bots</div>
      <div style={{ ...big, fontSize: 190, color: RED, marginTop: 4 }}>1 Pilot</div>
      <div style={{ marginTop: 26, background: RED, color: "white", fontFamily: "Helvetica, Arial, sans-serif", fontWeight: 900, fontSize: 46, padding: "10px 24px", borderRadius: 8, transform: "rotate(-2deg)", boxShadow: "0 8px 24px rgba(0,0,0,0.5)" }}>
        Who is flying yours?
      </div>
    </AbsoluteFill>

    {/* the speaker, framed like a "witness" card */}
    <div style={{ position: "absolute", right: 56, top: 70, width: 400, height: 520, transform: "rotate(2.5deg)", border: "8px solid white", borderRadius: 14, overflow: "hidden", boxShadow: "0 14px 40px rgba(0,0,0,0.65)" }}>
      <Img src={staticFile("thumb_frame.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "80% 20%", transform: "scale(1.9)", transformOrigin: "76% 24%" }} />
    </div>
    <div style={{ position: "absolute", right: 70, bottom: 44, fontFamily: "Helvetica, Arial, sans-serif", fontWeight: 800, fontSize: 30, color: "white", background: "rgba(0,0,0,0.75)", padding: "6px 16px", borderRadius: 6 }}>
      Rifat Erdem Sahin
    </div>
  </AbsoluteFill>
);
