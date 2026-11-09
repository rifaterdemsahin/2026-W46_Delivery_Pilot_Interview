import { Composition, Still } from "remotion";
import { Edit } from "./Main";
import { Thumbnail, ThumbnailA, ThumbnailB, ThumbnailC } from "./Thumbnail";
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
    <Composition
      id="LinkedIn"
      component={Edit}
      defaultProps={{ mode: "linkedin" as const }}
      durationInFrames={totalFrames(timelines.linkedin)}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
    <Composition
      id="X"
      component={Edit}
      defaultProps={{ mode: "x" as const }}
      durationInFrames={totalFrames(timelines.x)}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
    <Still id="Thumbnail" component={Thumbnail} width={WIDTH} height={HEIGHT} />
    <Still id="ThumbnailA" component={ThumbnailA} width={WIDTH} height={HEIGHT} />
    <Still id="ThumbnailB" component={ThumbnailB} width={WIDTH} height={HEIGHT} />
    <Still id="ThumbnailC" component={ThumbnailC} width={WIDTH} height={HEIGHT} />
  </>
);
