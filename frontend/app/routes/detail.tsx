import LineChart from '~/charts/line';
import type { Route } from "./+types/detail";
import { useState } from "react";

import historical_data from "../raw_data/waterloo_historical.json";
import predicted_data from "../raw_data/waterloo_predicted.json";

export function meta({ }: Route.MetaArgs) {
  return [
    { title: "Weather Detail" },
    { name: "description", content: "View weather details" },
  ];
}

const tempData = [
  {
    "id": "forecast",
    "data": [
      { "x": "2025-10-05T00:00:00Z", "y": 0.18 },
      { "x": "2025-10-05T00:05:00Z", "y": 0.18 },
      { "x": "2025-10-05T00:10:00Z", "y": 0.23 },
      { "x": "2025-10-05T00:15:00Z", "y": 0.26 },
      { "x": "2025-10-05T00:20:00Z", "y": 0.25 },
      { "x": "2025-10-05T00:25:00Z", "y": 0.25 },
      { "x": "2025-10-05T00:30:00Z", "y": 0.25 },
      { "x": "2025-10-05T00:35:00Z", "y": 0.25 },
      { "x": "2025-10-05T00:40:00Z", "y": 0.25 },
      { "x": "2025-10-05T00:45:00Z", "y": 0.25 },
      { "x": "2025-10-05T00:50:00Z", "y": 0.25 },
      { "x": "2025-10-05T00:55:00Z", "y": 0.26 },
      { "x": "2025-10-05T01:00:00Z", "y": 0.26 },
      { "x": "2025-10-05T01:05:00Z", "y": 0.20 },
      { "x": "2025-10-05T01:10:00Z", "y": 0.08 },
      { "x": "2025-10-05T01:15:00Z", "y": 0.01 },
      { "x": "2025-10-05T01:20:00Z", "y": 0.01 },
      { "x": "2025-10-05T01:25:00Z", "y": 0.01 },
      { "x": "2025-10-05T01:30:00Z", "y": 0.02 },
      { "x": "2025-10-05T01:35:00Z", "y": 0.03 },
    ]
  },
  {
    "id": "5-year avg",
    "data": [
      { "x": "2025-10-05T00:00:00Z", "y": 0.17 },
      { "x": "2025-10-05T00:05:00Z", "y": 0.17 },
      { "x": "2025-10-05T00:10:00Z", "y": 0.20 },
      { "x": "2025-10-05T00:15:00Z", "y": 0.23 },
      { "x": "2025-10-05T00:20:00Z", "y": 0.20 },
      { "x": "2025-10-05T00:25:00Z", "y": 0.20 },
      { "x": "2025-10-05T00:30:00Z", "y": 0.20 },
      { "x": "2025-10-05T00:35:00Z", "y": 0.21 },
      { "x": "2025-10-05T00:40:00Z", "y": 0.21 },
      { "x": "2025-10-05T00:45:00Z", "y": 0.22 },
      { "x": "2025-10-05T00:50:00Z", "y": 0.20 },
      { "x": "2025-10-05T00:55:00Z", "y": 0.23 },
      { "x": "2025-10-05T01:00:00Z", "y": 0.23 },
      { "x": "2025-10-05T01:05:00Z", "y": 0.15 },
      { "x": "2025-10-05T01:10:00Z", "y": 0.05 },
      { "x": "2025-10-05T01:15:00Z", "y": 0.00 },
      { "x": "2025-10-05T01:20:00Z", "y": 0.00 },
      { "x": "2025-10-05T01:25:00Z", "y": 0.0 },
      { "x": "2025-10-05T01:30:00Z", "y": 0.0 },
      { "x": "2025-10-05T01:35:00Z", "y": 0.01 },
    ]
  },

]

const transformPreWeatherData = (data: any) => {
  return data.map((item: any) => ({
    x: item.timestamp,
    y: item.predicted_precipitation_mm
  }));
}

const transformHisWeatherData = (data: any) => {
  return data.map((item: any) => ({
    x: item.timestamp,
    y: item.historical_avg_precipitation_mm
  }));
}

const data = [
  {
    "id": "forecast",
    "data": transformPreWeatherData(predicted_data.forecast)
  },
  {
    "id": "5-year avg",
    "data": transformHisWeatherData(historical_data.historical_baseline)
  },

]

export default function Detail() {
  return (
    <>
      <div className="container mx-auto px-4 py-8">
        <h2 className="text-white text-2xl font-bold mb-6 text-gray-900 dark:text-gray-100 text-center">
          Waterloo, ON, Canada, 2025-12-20 - 2025-12-27
        </h2>
        <p className="text-gray-200 dark:text-gray-400 p-2 m-1">
          Summary: Precipitation levels are lower than in previous years, temperatures are higher than usual, while air pressure and visibility remain consistent with past years.
        </p>

        <div className="flex justify-center align-center flex-wrap gap-4">
          <LineChart data={data} xAxisLabel="Time" yAxisLabel="Precipitation" />
          <LineChart data={tempData} xAxisLabel="Time" yAxisLabel="Temperature" />
          <LineChart data={tempData} xAxisLabel="Time" yAxisLabel="Pressure" />
          <LineChart data={tempData} xAxisLabel="Time" yAxisLabel="Cloudiness" />
        </div>
      </div>
    </>
  );
}
