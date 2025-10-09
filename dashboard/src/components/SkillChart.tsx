import { useState } from "react";
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

const FIRST_DATE = new Date("2025-01-01");
const LAST_DATE = new Date("2025-12-31");

export default function SkillChart({ data, sx }: SkillChartProps) {
  const firstDate = data.length > 0 ? data[0].datetime : FIRST_DATE;
  const lastDate = data.length > 0 ? data[data.length - 1].datetime : LAST_DATE;

  const [sliderValue, setSliderValue] = useState<number[]>([
    firstDate.getTime(),
    lastDate.getTime(),
  ]);

  const handleSliderChange = (
    _: Event,
    newValue: number | number[],
    activeThumb: number
  ) => {
    if (!Array.isArray(newValue)) {
      return;
    }
    if (newValue[1] - newValue[0] < 86400000) {
      if (activeThumb === 0) {
        const clamped = Math.min(newValue[0], LAST_DATE.getTime() - 86400000);
        setSliderValue([clamped, clamped + 86400000]);
      } else {
        const clamped = Math.max(newValue[1], FIRST_DATE.getTime() + 86400000);
        setSliderValue([clamped - 86400000, clamped]);
      }
    } else {
      setSliderValue(newValue as number[]);
    }
  };

  return (
    <Box
      sx={{
        width: sx?.width || "100%",
        display: "flex",
        alignItems: "center",
        flexDirection: "column",
        height: sx?.height || "100%",
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
          { dataKey: "mu", label: "Skill", stack: "total", color: "blue" },
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
        yAxis={[{ label: "Skill" }]}
        grid={{ vertical: true, horizontal: true }}
        sx={{ width: "100%", height: "100%" }}
      />
      <Slider
        value={sliderValue}
        valueLabelDisplay="off"
        min={FIRST_DATE.getTime()}
        max={LAST_DATE.getTime()}
        onChange={handleSliderChange}
        sx={{ width: "86%" }}
      />
    </Box>
  );
}
