import type { Route } from "./+types/home";
import { Search } from "../search/search";
import { useState, useEffect } from "react";
import * as feather from "feather-icons";

export function meta({ }: Route.MetaArgs) {
  return [
    { title: "New React Router App" },
    { name: "description", content: "Welcome to React Router!" },
  ];
}

interface SearchHistoryItem {
  id: string;
  place: string;
  address: string;
  startDate: string;
  endDate: string;
  precipitation: string;
  timestamp: Date;
  extreme: string;
}

export default function Home() {
  const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([
    {
      id: "1",
      place: "Waterloo, ON",
      address: "Waterloo, ON, Canada",
      startDate: "2025-12-20",
      endDate: "2025-12-27",
      precipitation: "18%",
      timestamp: new Date("2025-10-04T14:30:00"),
      extreme: "",
    },
    {
      id: "2",
      place: "Québec City, QC",
      address: "Québec City, QC, Canada",
      startDate: "2025-02-15",
      endDate: "2025-02-22",
      timestamp: new Date("2025-10-05T10:16:00"),
      precipitation: "82%",
      extreme: "Snowstorm",
    },
    {
      id: "3",
      place: "Vancouver, BC",
      address: "Vancouver, BC, Canada",
      startDate: "2026-04-20",
      endDate: "2026-04-25",
      timestamp: new Date("2025-10-05T13:45:00"),
      precipitation: "60%",
      extreme: "Heavy rain",
    },
  ]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const formatTimestamp = (date: Date) => {
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  };

  const getWeatherIcon = (precipitation: string) => {
    const precipValue = parseInt(precipitation);
    if (precipValue >= 70) {
      return "cloud-rain";
    } else if (precipValue >= 40) {
      return "cloud-drizzle";
    } else if (precipValue >= 20) {
      return "cloud";
    } else {
      return "sun";
    }
  };

  useEffect(() => {
    feather.replace();
  }, [searchHistory]);

  return (
    <>
      <Search />
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <h2 className="text-1xl text-white font-bold mb-6 text-gray-900 dark:text-gray-100">
          Search History
        </h2>
        <div className="space-y-4">
          {searchHistory.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400 text-center py-8">
              No search history yet
            </p>
          ) : (
            searchHistory.map((item) => (
              <div
                key={item.id}
                className="bg-white/70 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-lg p-3 shadow-sm hover:shadow-md transition-shadow relative"
              >
                <div className="flex justify-between items-start item-history">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-3">
                      <i
                        data-feather={getWeatherIcon(item.precipitation)}
                        className="text-blue-500 dark:text-blue-400"
                        style={{ width: "20px", height: "20px" }}
                      />
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {item.address}
                      </p>
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-700 dark:text-gray-300">
                          Date Range:
                        </span>
                        <span className="text-gray-600 dark:text-gray-400">
                          {formatDate(item.startDate)} - {formatDate(item.endDate)}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-700 dark:text-gray-300">
                          Precipitation:
                        </span>
                        <span className="text-gray-600 dark:text-gray-400">
                          {item.precipitation}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    {formatTimestamp(item.timestamp)}
                  </div>
                </div>
                {item.extreme && (
                  <div className="absolute bottom-2 right-2">
                    <span
                      className="px-2 py-1 text-xs font-medium text-white rounded"
                      style={{ backgroundColor: "#8E1100" }}
                    >
                      {item.extreme}
                    </span>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );
}
