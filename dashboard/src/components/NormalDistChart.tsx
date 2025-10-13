import { useMemo } from "react";
import { LineChart } from "@mui/x-charts";
import type { Rank } from "../types";


export interface NormalDistChartProps {
  ranks: Array<Rank>
  x?: {
    min?: number;
    max?: number;
  };
  height: number;
}

const LENGTH = 1000;

function norm_pdf(x: number, mu: number, sigma: number): number {
  const fraction = 1 / (sigma * Math.sqrt(2 * Math.PI));
  const exponent = -((x - mu) ** 2 / (2 * sigma ** 2));
  return fraction * Math.exp(exponent);
}

export default function NormalDistChart(props: NormalDistChartProps) {
  const [x, ys, min, max] = useMemo(() => {
    let lowestMu = Number.MAX_VALUE;
    let biggestMu = Number.MIN_VALUE;
    let biggestSigma = Number.MIN_VALUE;

    props.ranks.forEach((rank) => {
        if (rank.mu > biggestMu) biggestMu = rank.mu
        if (rank.mu < lowestMu) lowestMu = rank.mu
        if (rank.sigma > biggestSigma) biggestSigma = rank.sigma
    });

    const min = props.x?.min ?? ( lowestMu - 4 * biggestSigma);
    const max = props.x?.max ?? ( biggestMu + 4 * biggestSigma);
    const interval = (max - min) / LENGTH;

    const x = Array(LENGTH)
      .fill(undefined)
      .map((_, i) => i * interval + min);
    const ys = Array(props.ranks.length).fill(undefined).map((_, i) => {
        const mu = props.ranks[i].mu;
        const sigma = props.ranks[i].sigma;
        const y = x.map(value => norm_pdf(value, mu, sigma))
        return y
    })
    return [x, ys, min, max];
  }, [props]);

  return (
    <LineChart
      xAxis={[{ data: x , min: min, max: max, label: "skill"}]}
      series={
        ys.map(y => ({data: y, showMark: false}))
      }
      slotProps={{ tooltip: { trigger: "none" } }}
      height={props.height}
    />
  );
}
