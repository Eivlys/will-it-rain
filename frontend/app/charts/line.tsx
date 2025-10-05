import React from 'react';
import { ResponsiveLine } from '@nivo/line';

const LineChart = ({ data, xAxisLabel, yAxisLabel }: any) => {
    return (
        <div style={{ height: '350px', width: '600px', background: 'white' }}>
            <ResponsiveLine
                data={data}
                margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
                yScale={{ type: 'linear', min: 'auto', max: 'auto', stacked: true, reverse: false }}
                axisBottom={{ legend: xAxisLabel, legendOffset: 36 }}
                axisLeft={{ legend: yAxisLabel, legendOffset: -40 }}
                // pointSize={10}
                // pointColor={{ theme: 'background' }}
                // pointBorderWidth={2}
                // pointBorderColor={{ from: 'seriesColor' }}
                // pointLabelYOffset={-12}
                enableTouchCrosshair={true}
                useMesh={true}
                legends={[
                    {
                        anchor: 'bottom-right',
                        direction: 'column',
                        translateX: 100,
                        itemWidth: 80,
                        itemHeight: 22,
                        symbolShape: 'circle'
                    }
                ]}
            />
        </div>
    );
};

export default LineChart;