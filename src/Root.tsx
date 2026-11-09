import { Composition } from "remotion";
import { Main } from "./Main";
import { DURATION_FRAMES, FPS, HEIGHT, WIDTH } from "./config";

export const RemotionRoot = () => (
  <Composition
    id="Main"
    component={Main}
    durationInFrames={DURATION_FRAMES}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
  />
);
