export type Seat = { x: number; y: number; group: number };

const ROWS = 12;
const INNER_RADIUS = 0.35;
const CENTER_X = 100;
const CENTER_Y = 100;
const SCALE = 96;

function seatsPerRow(total: number): number[] {
  const radii = Array.from({ length: ROWS }, (_, row) => INNER_RADIUS + ((1 - INNER_RADIUS) * row) / (ROWS - 1));
  const sum = radii.reduce((acc, radius) => acc + radius, 0);
  const counts = radii.map((radius) => Math.floor((total * radius) / sum));
  let remainder = total - counts.reduce((acc, count) => acc + count, 0);
  for (let row = ROWS - 1; remainder > 0; row = row === 0 ? ROWS - 1 : row - 1) {
    counts[row] = (counts[row] ?? 0) + 1;
    remainder -= 1;
  }
  return counts;
}

export function hemicycleSeats(sizes: readonly number[]): Seat[] {
  const total = sizes.reduce((acc, size) => acc + size, 0);
  if (total === 0) {
    return [];
  }
  const counts = seatsPerRow(total);
  const raw = counts.flatMap((count, row) => {
    const radius = INNER_RADIUS + ((1 - INNER_RADIUS) * row) / (ROWS - 1);
    return Array.from({ length: count }, (_, index) => {
      const angle = count === 1 ? Math.PI / 2 : Math.PI - (Math.PI * index) / (count - 1);
      return { angle, radius };
    });
  });
  raw.sort((a, b) => b.angle - a.angle || a.radius - b.radius);
  const owners = sizes.flatMap((size, group) => Array.from({ length: size }, () => group));
  return raw.map((seat, index) => ({
    x: CENTER_X + SCALE * seat.radius * Math.cos(seat.angle),
    y: CENTER_Y - SCALE * seat.radius * Math.sin(seat.angle),
    group: owners[index] ?? 0,
  }));
}
