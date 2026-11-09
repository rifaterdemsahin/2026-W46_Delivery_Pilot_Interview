import { AbsoluteFill, Img, staticFile } from "remotion";

// public/visuals/thumb_bg.jpg   = fal.ai art (scripts/12_generate_thumbnail_art.py), committed
// public/thumb_frame.jpg        = frame from the 4K source (scripts/10_make_thumbnail.sh), git-ignored
const RED = "#ff2b2b";
const stroke = { WebkitTextStroke: "10px #000", paintOrder: "stroke fill" } as const;
const big = { fontFamily: "Impact, 'Arial Black', Helvetica, sans-serif", textTransform: "uppercase", lineHeight: 0.92, ...stroke } as const;

/** 1280x720 curiosity thumbnail: AI art of one pilot facing a wall of bots + a specific hook ("300 bots") + an open question. */
export const ThumbnailA = () => (
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

export const Thumbnail = ThumbnailA; // default (A)

const YELLOW = "#ffd400";
const bigB = { fontFamily: "Impact, 'Arial Black', Helvetica, sans-serif", textTransform: "uppercase", lineHeight: 0.9 } as const;

/** B: yellow/black pattern interrupt. An imperative ("Stop typing.") plus a big face. Tests: command + face close-up vs number + question. */
export const ThumbnailB = () => (
  <AbsoluteFill style={{ background: "#000" }}>
    <Img src={staticFile("visuals/thumb_B.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "brightness(1.15) saturate(1.3)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.55) 50%, rgba(0,0,0,0) 78%)" }} />
    <AbsoluteFill style={{ padding: "54px 0 0 52px", alignItems: "flex-start", justifyContent: "flex-start" }}>
      <div style={{ ...bigB, fontSize: 215, color: "#000", background: YELLOW, padding: "6px 28px 0", transform: "rotate(-3deg)", boxShadow: "0 10px 30px rgba(0,0,0,0.5)" }}>Stop</div>
      <div style={{ ...bigB, fontSize: 168, color: "white", marginTop: 14, WebkitTextStroke: "9px #000", paintOrder: "stroke fill" }}>Typing.</div>
      <div style={{ marginTop: 22, color: YELLOW, fontFamily: "Helvetica, Arial, sans-serif", fontWeight: 900, fontSize: 52, textShadow: "0 4px 14px #000" }}>Start directing AI.</div>
    </AbsoluteFill>
    <div style={{ position: "absolute", right: 0, top: 0, width: 520, height: 720, overflow: "hidden", borderLeft: `10px solid ${YELLOW}`, boxShadow: "-14px 0 40px rgba(0,0,0,0.7)" }}>
      <Img src={staticFile("thumb_frame_b.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "72% 20%", transform: "scale(1.65)", transformOrigin: "70% 30%" }} />
    </div>
  </AbsoluteFill>
);

const CYAN = "#19e3ff";
/** C: no face, identity question. Split screen "Driver" (grey) vs "Pilot" (cyan) + "Which are you?". Tests: no face + self-identification. */
export const ThumbnailC = () => (
  <AbsoluteFill style={{ background: "#05121a" }}>
    <AbsoluteFill style={{ clipPath: "polygon(0 0, 58% 0, 42% 100%, 0 100%)" }}>
      <Img src={staticFile("visuals/thumb_C_driver.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "grayscale(1) contrast(1.15) brightness(0.8)" }} />
      <AbsoluteFill style={{ background: "rgba(0,0,0,0.25)" }} />
    </AbsoluteFill>
    <AbsoluteFill style={{ clipPath: "polygon(58% 0, 100% 0, 100% 100%, 42% 100%)" }}>
      <Img src={staticFile("visuals/thumb_C_pilot.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "saturate(1.4) brightness(1.15)" }} />
    </AbsoluteFill>
    <AbsoluteFill style={{ clipPath: "polygon(57.4% 0, 58.6% 0, 42.6% 100%, 41.4% 100%)", background: CYAN, boxShadow: `0 0 30px ${CYAN}` }} />
    <div style={{ position: "absolute", left: 44, top: 36, ...bigB, fontSize: 150, color: "#d9d9d9", WebkitTextStroke: "9px #000", paintOrder: "stroke fill" }}>Driver</div>
    <div style={{ position: "absolute", right: 40, top: 36, ...bigB, fontSize: 190, color: CYAN, WebkitTextStroke: "9px #00141a", paintOrder: "stroke fill" }}>Pilot</div>
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 64, textAlign: "center" }}>
      <span style={{ ...bigB, fontSize: 112, color: "white", background: "rgba(0,0,0,0.78)", padding: "6px 34px", borderRadius: 14, border: `6px solid ${CYAN}` }}>Which are you?</span>
    </div>
    <div style={{ position: "absolute", right: 30, bottom: 16, fontFamily: "Helvetica, Arial, sans-serif", fontWeight: 800, fontSize: 24, color: "white", textShadow: "0 2px 8px #000" }}>Rifat Erdem Sahin · Delivery Pilot</div>
  </AbsoluteFill>
);
