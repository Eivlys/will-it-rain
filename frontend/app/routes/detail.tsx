import LineChart from '~/charts/line';
import type { Route } from "./+types/detail";
import { useState } from "react";

export function meta({ }: Route.MetaArgs) {
  return [
    { title: "Weather Detail" },
    { name: "description", content: "View weather details" },
  ];
}

const data = [
  {
    "id": "projection",
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
    "id": "historical",
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

export default function Detail() {
  return (
    <>
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-gray-100">
          Weather Detail
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Weather information will be displayed here.
        </p>
        <LineChart data={data} xAxisLabel="Time" yAxisLabel="Precipitation" />
        <LineChart data={data} xAxisLabel="Time" yAxisLabel="Temperature" />
        <LineChart data={data} xAxisLabel="Time" yAxisLabel="Pressure" />
        <LineChart data={data} xAxisLabel="Time" yAxisLabel="Cloudiness" />
      </div>
    </>
  );
}
