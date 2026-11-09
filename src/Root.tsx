import { Composition } from "remotion";
import { Edit } from "./Main";
import { FPS, HEIGHT, WIDTH } from "./config";
import { timelines, totalFrames } from "./edit";

export const RemotionRoot = () => (
  <>
    <Composition
      id="Main"
      component={Edit}
      defaultProps={{ mode: "main" as const }}
      durationInFrames={totalFrames(timelines.main)}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
    <Composition
      id="Highlights"
      component={Edit}
      defaultProps={{ mode: "highlights" as const }}
      durationInFrames={totalFrames(timelines.highlights)}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
    <Composition
      id="Combined"
      component={Edit}
      defaultProps={{ mode: "combined" as const }}
      durationInFrames={totalFrames(timelines.combined)}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
  </>
);
