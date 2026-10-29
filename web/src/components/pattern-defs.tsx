export const PatternDefs: React.FC = () => {
  return (
    <svg aria-hidden="true" width="0" height="0" className="absolute">
      <defs>
        <pattern id="pattern-contre" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <rect width="4" height="4" className="fill-bg" />
          <rect width="2" height="4" className="hatch-contre" />
        </pattern>
      </defs>
    </svg>
  );
};
