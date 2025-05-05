((window1, undefined) => {
  //
  const plotly = {
    add: function(elt, meta, items) {
      const series = []
      items.forEach(item => {
        series.push({
          name: item.name,
          x:    item.x_data,
          y:    item.y_data,
          // mode: 'lines+markers',
          mode: 'lines',
          line:   { color: item.color, width: 3 },
          marker: { color: item.color, size: 6 },
        })
      });
      Plotly.newPlot(
        elt,
        series,
        {
          title: { text: meta.title, font: { weight: 800 } },
          xaxis: { title: meta.xaxis },
          yaxis: { title: meta.yaxis },
          autosize: true,
          // showlegend: false,
          // legend: {
          //   x: 1,
          //   xanchor: 'right',
          //   y: 1
          // }
          // margin: {
          //   l: 10,
          //   r: 10,
          //   b: 10,
          //   t: 10,
          //   pad: 0,
          // },          
        }
      );
    },
    add_ys: function(elt, meta, x_data, y_items) {
      this.add(elt, meta, y_items.map((item) => {return {name: item.name, color: item.color, x_data: x_data, y_data: item.data} } ))
    },
    upd_y: function(elt, y_index, y_data) {
      Plotly.restyle(elt, { 'y': [y_data] }, [y_index]);
    },
    upd_y_all: function(elt, y_data_arr) {
      Plotly.restyle(elt, { 'y': y_data_arr });
    },
  };
  // global
  if(window1.chartlibs === undefined) window1.chartlibs = {};
  window1.chartlibs.plotly = plotly;
  //
})(window);