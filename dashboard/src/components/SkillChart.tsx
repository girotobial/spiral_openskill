import { useState, useMemo, useEffect } from "react";
import { Slider, Box } from "@mui/material";
import { LineChart } from "@mui/x-charts";

export interface SkillChartProps {
  data: Array<{
    datetime: Date;
    mu: number;
    lowerBound: number;
    upperBound: number;
  }>;
  sx?: {
    width?: string | number;
    height?: string | number;
  }
}

const FALLBACK_FIRST = new Date("2025-01-01");
const FALLBACK_LAST = new Date("2025-12-31");
const ONE_DAY_MS = 86_400_000;

export default function SkillChart({ data, sx }: SkillChartProps) {

  const [minTs, maxTs] = useMemo(() => {
    if (data.length === 0) {
      return [FALLBACK_FIRST.getTime(), FALLBACK_LAST.getTime()];
    }
    const first = data[0].datetime.getTime();
    const last = data[data.length - 1].datetime.getTime();
    return [first, last];
  }, [data]);


  const [sliderValue, setSliderValue] = useState<number[]>([
    minTs, maxTs
  ]);

  useEffect(() => {
    setSliderValue(([currStart, currEnd]) => [
      Math.max(minTs, Math.min(currStart, maxTs)),
      Math.max(minTs, Math.min(currEnd, maxTs))
    ]
  );
  },[minTs, maxTs]);

  const handleSliderChange = (
    _: Event,
    newValue: number | number[],
  ) => {
    if (!Array.isArray(newValue)) {
      return;
    }
    setSliderValue(newValue)
  };

  const tooShort = maxTs - minTs < ONE_DAY_MS;


  return (
    <Box
      sx={{
        width: sx?.width || "100%",
        display: "flex",
        alignItems: "center",
        flexDirection: "column",
        height: sx?.height ?? 420
      }}
    >
      <LineChart
        series={[
          {
            dataKey: "lowerBound",
            showMark: false,
            color: "grey",
            label: "95% Lower Bound",
          },
          { dataKey: "mu", label: "Skill", color: "blue" },
          {
            dataKey: "upperBound",
            showMark: false,
            color: "grey",
            label: "95% Upper Bound",
          },
        ]}
        dataset={data}
        xAxis={[
          {
            dataKey: "datetime",
            scaleType: "time",
            label: "Date/Time",
            min: new Date(sliderValue[0]),
            max: new Date(sliderValue[1]),
          },
        ]}
        yAxis={[{ label: "'Open Skill' Ability Estimate" }]}
        grid={{ vertical: true, horizontal: true }}
        sx={{ width: "100%", height: "90%" }}
      />
      <Slider
        value={sliderValue}
        valueLabelDisplay="off"
        min={minTs}
        max={maxTs}
        onChange={handleSliderChange}
        step={ONE_DAY_MS}
        sx={{ width: "86%", height: "10%" }}
        aria-label="Date Range"
        disableSwap
        disabled={tooShort}
      />
    </Box>
  );
}
