var smt_syscharts = `
<div class="chartcol"><img class="chartimg" id="barChart" src="/static/smartchart/editor/echart/img/bar.webp"></div>
<div class="chartcol"><img class="chartimg" id="lineChart" src="/static/smartchart/editor/echart/img/line.webp"></div>
<div class="chartcol"><img class="chartimg" id="pieChart" src="/static/smartchart/editor/echart/img/pie.webp"></div>
<div class="chartcol"><img class="chartimg" id="gaugeChart" src="/static/smartchart/editor/echart/img/gauge.webp"></div>
<div class="chartcol"><div class="iconfont iconrefresh1 chartimg" id="lastChart">恢复原始</div></div>
<div class="chartcol"><div class="iconfont iconmianban chartimg" id="h1Chart">大字报</div></div>
<div class="chartcol"><div class="iconfont icondanganziliao-biaogetianxie chartimg" id="excelChart">Excel表格</div></div>
<div class="chartcol"><div class="iconfont iconbiaoge chartimg" id="tableChart">表格</div></div>
<div class="chartcol"><div class="iconfont iconbiaoge chartimg" id="vuetableChart">VUE表格</div></div>
<div class="chartcol"><div class="iconfont iconditu chartimg" id="mapChart">中国地图</div></div>
<div class="chartcol"><div class="iconfont iconleidatu chartimg" id="radarChart">雷达图</div></div>
<div class="chartcol"><div class="iconfont iconchartwordcloud chartimg" id="wordChart">词云图</div></div>
<div class="chartcol"><div class="iconfont iconchart-trend-full chartimg" id="diyChart">线柱图</div></div>
<div class="chartcol"><div class="iconfont iconchart-trend-full chartimg" id="dlineChart">细节线图</div></div>
<div class="chartcol"><div class="iconfont iconicon-test chartimg" id="mutiChart">多区域图</div></div>
<div class="chartcol"><div class="iconfont iconlunbobiaoge chartimg" id="liMTable">滚动表格</div></div>
<div class="chartcol"><div class="iconfont icontimelinechart chartimg" id="timelinechart">时间轴图</div></div>
<div class="chartcol"><div class="iconfont iconline-slideshowhuandengpianfangying-02 chartimg" id="swaperTable">连播图</div></div>
<div class="chartcol"><div class="iconfont iconbiaodanzujian-xialakuang chartimg" id="filterChart">筛选器</div></div>
<div class="chartcol"><div class="iconfont iconloudoutu chartimg" id="funnelChart">漏斗图</div></div>
<div class="chartcol"><div class="iconfont iconsandiantu chartimg" id="scatterChart">散点图</div></div>
<div class="chartcol"><div class="iconfont iconvuejs chartimg" id="vueChart">VUE</div></div>
<div class="chartcol"><div class="iconfont iconbiaoge chartimg" id="lineUpChart">lineUp图</div></div>
<div class="chartcol"><div class="iconfont iconPipedepth chartimg" id="drillchart">钻取图</div></div>
<div class="chartcol"><div class="iconfont icontime chartimg" id="timechart">时间</div></div>
<div class="chartcol"><div class="iconfont icondanganziliao-biaogetianxie chartimg" id="pivotchart">透视图</div></div>
<div class="chartcol"><div class="iconfont iconrilitu chartimg" id="calendarChart">日历图</div></div>
<div class="chartcol"><div class="iconfont icongantetu chartimg" id="gantChart">甘特图</div></div>
<div class="chartcol"><div class="iconfont iconjizuobiaotu chartimg" id="corChart">极坐标</div></div>
<div class="chartcol"><div class="iconfont iconed_div chartimg" id="qrChart">二维码</div></div>`;

var barChart = `let series =[];
let dataset = __dataset__;
for (let i=1;i<dataset[0].length;i++){
    series.push({
        type: 'bar',
        itemStyle: {
            borderRadius: 6,
         },
        emphasis:{
            focus: "data"
        },
        //stack: 'A', //开启堆叠
      }
    )
}

option__name__= {
    dataset:{source:dataset },
    title: {
        text: "",
        textStyle: {
         fontSize: '20px',
       },
    },
    legend: {
        show:true,
        textStyle: {
         fontSize: "12px",
       },
    },
    tooltip: {},
    xAxis: {
        type: 'category',
        axisLabel: {
            textStyle: {
                fontSize:"12px"
            }
       },
    },
    yAxis: {
        type: 'value',
        axisLabel: {
            textStyle: {
                fontSize:"12px"
            }
       },
    },
    series: series
};
`;

var lineChart =`let series =[];
let dataset = __dataset__;
for (let i=1;i<dataset[0].length;i++){
    series.push({
        type: 'line',
        smooth: true,
        //stack: 'A', //开启堆叠
        //areaStyle: {}, //面积图
        //step:'start', //阶梯图middle,end
      }
    )
}

option__name__= {
    dataset:{source:dataset },
    title: {
        text: "",
        textStyle: {
         fontSize: "20px",
       },
    },
    legend: {
        show:true,
        textStyle: {
         fontSize: "12px",
       },
    },
    tooltip: {},
    xAxis: {
        type: 'category',
        axisLabel: {
            textStyle: {
                fontSize:"12px"
            }
       },
    },
    yAxis: {
        type: 'value',
        axisLabel: {
            textStyle: {
                fontSize:"12px"
            }
       },
    },
    series: series
};
`;

var pieChart =`let dataset = __dataset__; 
let series =[];
for (let i=1;i<dataset.length;i++){
    series.push({
        name: dataset[i][0],
        value: dataset[i][1],
        emphasis:{
            focus: "data"
        }
    })
}

option__name__ = {
    title: {
        text: dataset[0][1],
        left: 'center',
        top: 20,
        textStyle: {
            fontSize: "20px"
        }
    },
    tooltip : {
        trigger: 'item',
    },
    series : [
        {
            name:dataset[0][1],
            type:'pie',
            radius : ['10%', '55%'],
            center: ['50%', '50%'],
            roseType: 'radius', 
            label: {
                textStyle: {
                    fontSize: "12px"
                }
            },
            itemStyle: {
                borderRadius: 6
            },
            data: series
        }
    ]
};
`;

var gaugeChart = `let dataset=__dataset__;
option__name__={ 
    tooltip : {},
    title:{
        text:''
    },
    series: [
    {
        name: dataset[0][1],
        type: 'gauge',
        min: 0,
        max: dataset[1][2],
        splitNumber: 10,
        axisLabel:{
           fontSize: "6px" 
        },
        axisTick:{
            distance: 2,
            length: "24px",
            splitNumber: 5
        },
        splitLine:{
            distance: 8,
            length: "5%"
        },
        pointer:{
            icon: '', //circle,rect,roundRect,triangle,diamond,pin,arrow
            length: '60%',
            width: 6
        },
        detail: {
            formatter:'{value}',
            textStyle:{
                fontSize:"12px"
            },
        },
        data: [
            {value: dataset[1][1],name:dataset[1][0],
             title:{
                show: true,
                fontSize: "10px"
           }
        }]
    }
    ]                        
 };
`;

var filterChart = `let dataset=__dataset__;
let table =\`
<label style="margin-right:5px">选择</label>
<select id="id_select__name__"
 style="width:100px;height:25px;">
\`;
table = table + '<option value="" selected>----</option>';
 for(let i=1;i<dataset.length;i++){ 
  table = table + '<option>' + dataset[i][0] + '</option>';
 }
table = table + '</select>'

dom__name__.innerHTML=table;
`;

var tableChart = `let dataset=__dataset__;
let table = '<div ><table class="table">';
//头部
table += '<thead ><tr>';
for(let j=0; j<dataset[0].length;j++){
  table = table + "<td>" + dataset[0][j] + "</td>";
};
table += "</tr></thead>";

//表主体
table += "<tbody>";
 for(let i=1;i<dataset.length;i++){
    if(i%2==0){table += "<tr style='background-color:#cfe2f3'>";}
     else{table += "<tr>"};
    for (j=0; j<dataset[i].length;j++){
       table = table + "<td>" + dataset[i][j] + "</td>";
      };
      table += "</tr>";
 };
 table += "</tbody></table></div>";

dom__name__.innerHTML=table;`;

var vueChart = `vapp.d__name__ = __dataset__;`;

var diyChart = `let dataset = __dataset__; 
let legend_label = ds_rowname(dataset);
let xlabel = dataset[0].slice(1);
dataset = ds_createMap(dataset);

option__name__  = {
   title: {
       text: '',
       left: 'center'
    }, 
    tooltip: {
       trigger: 'item',
       formatter: '{a} <br/>{b} : {c}' 
    },
    legend: {
       left: 'center',
       data: legend_label
    }, 
    xAxis: {
       type: 'category',
       data: xlabel
    }, 
    //多Y轴
    yAxis: [{
        type: 'value',
        name:'',
        position:'left'
    },{
        type: 'value',
        name:'差异',
        position : 'right'
    }],
    
   series: [{
        name: legend_label[0],
        data: dataset[legend_label[0]],
        type: 'bar'
   },
   {
        name: legend_label[1],
        data: dataset[legend_label[1]],
        type: 'line',
        yAxisIndex:1 //定义坐标
    }
 ]
};`;

var h1Chart=`let dataset = __dataset__;
let table = \`
<div style="background-color:white;text-align:center;height:100%">
<h1>\${dataset[0][0]}</h1>
<h3>\${dataset[1][0]}</h3>
</div>
\`;
dom__name__.innerHTML=table;
`;

var mutiChart = `let dataset = __dataset__; 
let legend_label = ds_rowname(dataset);
let xlabel = dataset[0].slice(1);
dataset = ds_createMap(dataset);

option__name__= {
  title: [
    {
      left: '20%',
      text: legend_label[0]
    },
    {
      right: '25%',
      text: legend_label[1]
    },
    {
      left: '20%',
      bottom: '50%',
      text: legend_label[2]
    },
    {
      right: '25%',
      bottom: '50%',
      text: legend_label[3]
    }
  ],
  tooltip: {
    trigger: 'axis'
  },
  xAxis: [
    {
      data: xlabel
    },
    {
      data: xlabel,
      gridIndex: 1
    },
    {
      data: xlabel,
      gridIndex: 2
    },
    {
      data: xlabel,
      gridIndex: 3
    }
  ],
  yAxis: [
    {},
    {
      gridIndex: 1
    },
    {
      gridIndex: 2
    },
    {
      gridIndex: 3
    }
  ],
  grid: [
    {
      bottom: '60%',
      right: '55%'
    },
    {
      bottom: '60%',
      left: '55%'
    },
    {
      top: '60%',
      right: '55%'
    },
    {
      top: '60%',
      left: '55%'
    },
  ],
  series: [
    {
      type: 'line',
      showSymbol: false,
      data: dataset[legend_label[0]]
    },
    {
      type: 'bar',
      showSymbol: false,
      data: dataset[legend_label[2]],
      xAxisIndex: 1,
      yAxisIndex: 1
    },
    {
      type: 'bar',
      showSymbol: false,
      data: dataset[legend_label[3]],
      xAxisIndex: 2,
      yAxisIndex: 2
    },
    {
      type: 'line',
      showSymbol: false,
      data: dataset[legend_label[3]],
      xAxisIndex: 3,
      yAxisIndex: 3
    }
  ]
};`;

var liMTable= `let dataset = __dataset__; 
let tablehead = '';
let tablebody = '';

for(i=0;i<dataset[0].length; i++){
    tablehead = \`\${tablehead}<span>\${dataset[0][i]}</span>\`;
}

for(let i=1; i<dataset.length; i++){
    let temp='';
    for(let j=0; j<dataset[i].length; j++){
        temp=\`\${temp\}<span>\${dataset[i][j]}</span>\`;
    }
    tablebody=\`\${tablebody}<li>\${temp}</li>\`;
}

let table =\`
<div class="smtlisthead">\${tablehead}</div>
<div class="smtlistnav smtlist__name__">
 <ul>\${tablebody}</ul>
</div>\`;
dom__name__.innerHTML=table;

ds_scroll('.smtlist__name__', interval = 1000, step = 10);
//ds_liMarquee('.smtlist__name__');
`;

var swaperTable = `let dataset = __dataset__;
dataset = [['url'],['/static/smartui/img/smartlogo.png'],['/static/smartui/img/smartviplogo.png']];
let myslides='';

for(i=1;i<dataset.length;i++){
    myslides = \`\$\{myslides\}<div class="swiper-slide"><img src ="\$\{dataset[i][0]\}"></div>\`;
}

let table = \`<div class="swiper swiper__name__" style="height:100%">
<div class="swiper-wrapper">\$\{myslides\}</div></div>\`;
dom__name__.innerHTML=table;

ds_swiper('.swiper__name__');
`;
var lineUpChart = `ds_loadcss('smt_LineUp');
ds_loadjs('smt_LineUp');
let dataset = __dataset__;
dataset = ds_createMap_all(dataset);
try{Ljs__name__.destroy()}catch{}
Ljs__name__ = LineUpJS.asLineUp(dom__name__, dataset);
`;
var funnelChart = `let dataset = __dataset__;
let legend_label = ds_rowname(dataset);
let series =[];
for (let i=1;i<dataset.length;i++){
    series.push({name: dataset[i][0],value: dataset[i][1]})
}

option__name__={
    tooltip: {
        trigger: 'item',
        formatter: "{c}"
    },
    calculable: true,
    series: [
        {
            type:'funnel',
            left: '10%',
            top: 60,
            bottom: 60,
            width: '80%',
            min: 0,
            max: 100,
            minSize: '0%',
            maxSize: '100%',
            sort: 'descending',
            gap: 2,
            label: {
                show: true,
                position: 'inside'
            },
            labelLine: {
                length: 10,
                lineStyle: {
                    width: 1,
                    type: 'solid'
                }
            },
            itemStyle: {
                borderColor: '#fff',
                borderWidth: 1
            },
            emphasis: {
                label: {
                    fontSize: 20
                }
            },
            data: series
        }
    ]                                    
};`;

var scatterChart=`let dataset=__dataset__;
dataset=[['x','y'],[10,12],[11,15],[20,31]];
option__name__ = {
    title: {
        text:dataset[0][0]
    },
    xAxis: {},
    yAxis: {},
    series: [{
        symbolSize: 20,
        data: dataset ,
        type: 'scatter'
    }]
};
`;

var excelChart=`let dataset = __dataset__;
let options = {
    view: true,  //查看发布
    dev_mode: true, //开发方式
    allowEdit:true, //可编辑
    //plugins: ['chart'], //启用图形
};
ds_excel_upload('__name__', dataset, options);
`;

var wordChart=`//select 词名,数量
//需多点一次运行查看,仪表中显示需先在"模板"-->资源中加载词云js文件
ds_loadjs('smt_wordcloud');
let dataset = __dataset__;
let legend_label = ds_rowname(dataset);
dataset = ds_createMap(dataset);

let series=[];
for (let i=0;i<legend_label.length;i++){
 series.push({name:legend_label[i],value:dataset[legend_label[i]]})
}

option__name__={
tooltip: {
        show: true
    },
    series: [{
        type: 'wordCloud',
        sizeRange: [6, 88],//画布范围，如果设置太大会出现少词（溢出屏幕）
        rotationRange: [-45, 90],//数据翻转范围
        //shape: 'circle',
        textPadding: 0,
        autoSize: {
            enable: true,
            minSize: 6
        },
        textStyle: {
                color: function() {
                    return 'rgb(' + [
                        Math.round(Math.random() * 160),
                        Math.round(Math.random() * 160),
                        Math.round(Math.random() * 160)
                    ].join(',') + ')';
            },
            emphasis: {
                shadowBlur: 10,
                shadowColor: '#333'
            }
        },
        data:series 
        }]
                                     
};`;
var radarChart=`//select 维度,指标1, 指标2,..., 目标  注意最后一列是目标
let dataset = __dataset__; 
dataset = ds_transform(dataset);
legend_label = ds_rowname(dataset);
let title=dataset[0][0];
let xlabel = dataset[0].slice(1);
dataset = ds_createMap(dataset);
let indicator=[];
let series=[];
let target = dataset[legend_label.pop()];
for(i=0; i<target.length;i++){
    indicator.push({name:xlabel[i],max:target[i]})
}
for(i=0; i<legend_label.length;i++){
    series.push({value:dataset[legend_label[i]],name:legend_label[i]});
}

option__name__ = {
    title: {
        text: title
    },
    tooltip: {},
    legend: {
        data: legend_label
    },
    radar: {
        // shape: 'circle',
        name: {
            textStyle: {
                color: '#fff',
                backgroundColor: '#999',
                borderRadius: 3,
                padding: [3, 5]
           }
        },
        indicator:indicator
    },
    series: [{
        name: title ,
        type: 'radar',
        // areaStyle: {normal: {}},
        data :series
    }]
};
`;
var mapChart=`//select province, value
ds_loadjs('smt_china')
//设置值范围
let minvalue=0;
let maxvalue=6000;
let dataset = __dataset__;
let title = dataset[0][0];
let series=[];
for (let i=1;i<dataset.length;i++){
 series.push({name:dataset[i][0],value:dataset[i][1]})
}

option__name__ = {
\ttitle: {},
\ttooltip : {
\t\ttrigger: 'item'
\t},
    dataRange: {
\t\t\tmin : minvalue,
\t\t\tmax : maxvalue,
\t\t\tcalculable : true,
            //orient : horizontal,
\t\t//\tcolor: ['#ff3333', 'orange', 'yellow','lime','aqua'],
\t\t\ttextStyle:{
\t\t\t//\tcolor:'#fff'
\t\t\t}},

    series: [
        {
\t\tname: title,
\t\ttype: 'map',
\t\tmapType: 'china',
\t\troam: false,
\t\tlabel: {
\t\t\tnormal: {
\t\t\t\tshow: true
\t\t\t},
\t\t\temphasis: {
\t\t\t\tshow: false
\t\t\t}
\t\t},
\t\tdata:series
\t}
        ]
    };
`;
var pivotchart=`let dataset=__dataset__;
ds_loadpivot(); //透视图需购买专业版
let pivotOption = {
    rendererName:'表格',
    aggregatorName: '求和',
    rows: [],cols: [],vals:[],
    rendererOptions:{table:{rowTotals: false,colTotals:true}},
    showUI: true
};
$(dom__name__).pivotUI(dataset, pivotOption,true);`;

var timelinechart=`//select 维度,指标1,指标2,指标3...
let dataset = __dataset__; 
legend_label = ds_rowname(dataset);
xlabel = dataset[0].slice(1);
dataset = ds_createMap(dataset);

let series =[];
for (let i=0;i<legend_label.length;i++){
    series.push({
        title: {
             text: legend_label[i]
         },
        series: [
            {
                data: dataset[legend_label[i]],
            },
        ]
    });
}

option__name__= {
    baseOption: {
        timeline: {
            //loop: false,        
            axisType: 'category',
            show: true,
            autoPlay: true,
            playInterval: 2000,
            data: legend_label
        },
        xAxis: [{type: 'category',name: 'day',data: xlabel}],
        yAxis: { type: 'value', name: 'qty' },
        series: [{type: 'bar'}],
        tooltip: {}
    },
    options:series
}`;

var drillchart=`//select 大类,值;select 大类,小类,值
let dataset = __dataset__; 
df0 = dataset.df0;
df1 = dataset.df1;

let xdata =[];
let seriesdata = [];
let drilldownData = [];
let kv = new Map();
for (let i=1;i<df1.length;i++){
    if(kv.hasOwnProperty(df1[i][0])){
        kv[df1[i][0]].push(df1[i].slice(1));
    }else{
        kv[df1[i][0]] = [df1[i].slice(1)];
    }
}

for (i=1;i<df0.length;i++){
    xdata.push(df0[i][0]);
    seriesdata.push({
        value: df0[i][1],
        groupId: df0[i][0]
      });
    drilldownData.push({
    dataGroupId: df0[i][0],
    data: kv[df0[i][0]]
     });
}

option__name__= {
  xAxis: {
    data: xdata
  },
  yAxis: {},
  dataGroupId: '',
  animationDurationUpdate: 500,
  series: {
    type: 'bar',
    id: 'sales',
    data:seriesdata,
    universalTransition: {
      enabled: true,
      divideShape: 'clone'
    }
  }
};

myChart__name__.on('click', event => {
  if (event.data) {
    const subData = drilldownData.find(data => {
      return data.dataGroupId === event.data.groupId;
    });
    if (!subData) {
      return;
    }
    myChart__name__.setOption({
      xAxis: {
        data: subData.data.map(item => {
          return item[0];
        })
      },
      series: {
        type: 'bar',
        id: 'sales',
        dataGroupId: subData.dataGroupId,
        data: subData.data.map(item => {
          return item[1];
        }),
        universalTransition: {
          enabled: true,
          divideShape: 'clone'
        }
      },
      graphic: [
        {
          type: 'text',
          left: 50,
          top: 20,
          style: {
            text: '返回',
            fontSize: 18
          },
          onclick: function() {
            myChart__name__.setOption(option__name__, true);
          }
        }
      ]
    });
  }
});
myChart__name__.setOption(option__name__);`

var timechart=`let t = setTimeout(time,1000);
function time()
{
   clearTimeout(t);
   let dt = new Date();
   let y=dt.getFullYear();
   let mt=dt.getMonth()+1;
   let day=dt.getDate();
   let h=dt.getHours();
   let m=dt.getMinutes();
   let s=dt.getSeconds();
   dom__name__.innerHTML = y+"年"+mt+"月"+day+"-"+h+"时"+m+"分"+s+"秒";
   t = setTimeout(time,1000);
}`;

var vuetableChart=`
let df0 = __dataset__;
//处理表头
let columnsDict = {'c1':'渠道','qty':'数量'};
let tableHead = [];
let tableHeadLabel;
for (let i=0;i<df0[0].length;i++){
    if(columnsDict.hasOwnProperty(df0[0][i])){
        df0[0][i] = columnsDict[df0[0][i]]
    }
    tableHeadLabel=df0[0][i];
    tableHead.push({label: tableHeadLabel, prop:df0[0][i]});
}

//VUE赋值,在模板中加入表格组件
vapp.d0 = {tableHead:tableHead,tableData:ds_createMap_all(df0)};
`;
var calendarChart=`//select 日期, 值
let dataset = __dataset__; 
dataset= dataset.slice(1);
dataset = [['2019-10-01',12],['2019/10/02',1000]];
let month = dataset[1][0].substring(0,7);
option__name__= {
    tooltip: {
        position: 'top'
    },
    visualMap: {
        show: false,
        min: 0,
        max: 1000
    },
    calendar: [{
        left: 'center',
        top: 'middle',
        cellSize: [30, 30],
        yearLabel: {show: true},
        orient: 'vertical',
        dayLabel: {
            firstDay: 1,
            nameMap: 'cn'
        },
        monthLabel: {
            show: true
        },
        range: month
    }],
    series: {
        type: 'heatmap',
        coordinateSystem: 'calendar',
        data: dataset
    }
};`;
var gantChart=`// select 项目名, 开始时间, 结束时间
let dataset = __dataset__; 
let legend_label = ds_rowname(dataset);
dataset = ds_createMap(dataset);

let series =[];
for (let i=0;i<legend_label.length;i++){
    series.push(
        {
            name: legend_label[i],
            type: "bar",
            stack: legend_label[i],
            label: {
                normal: {
                    show: true,
                    color: "#000",
                    position: "right",
                    formatter: function(params) {
                        return params.seriesName
                    }
                }
            },
            itemStyle: {
                normal: {
                    color: "skyblue",
                    borderColor: "#fff",
                    borderWidth: 2
                }
            },
            zlevel: -1,
            data: [new Date(dataset[legend_label[i]][1])]
        },
        {
            name: legend_label[i],
            type: "bar",
            stack: legend_label[i],
            itemStyle: {
                normal: {
                    color: "white",
                }
            },
            zlevel: -1,
            z: 3,
            data:[new Date(dataset[legend_label[i]][0])]
        }
        );
}
option__name__= {
    backgroundColor: "#fff",
    title: {
        text: "甘特图",
        padding: 20,
        textStyle: {
            fontSize: 17,
            fontWeight: "bolder",
            color: "#333"
        },
        subtextStyle: {
            fontSize: 13,
            fontWeight: "bolder"
        }
    },
    legend: {
        data:legend_label,
        align: "right",
        right: 80,
        top: 50
    },
    grid: {
        containLabel: true,
        show: false,
        right: 130,
        left: 40,
        bottom: 40,
        top: 90
    },
    xAxis: {
        type: "time",
        axisLabel: {
            "show": true,
            "interval": 0
        }
    },
    yAxis: {
        axisLabel: {
            show: true,
            interval: 0,
            formatter: function(value, index) {
                let last = ""
                let max = 5;
                let len = value.length;
                let hang = Math.ceil(len / max);
                if (hang > 1) {
                    for (let i = 0; i < hang; i++) {
                        let start = i * max;
                        let end = start + max;
                        let temp = value.substring(start, end) + "\\n";
                        last += temp;
                    }
                    return last;
                } else {
                    return value;
                }
            }
        },
        data: ["维度"]
    },
    tooltip: {
        trigger: "axis",
        formatter: function(params) {
            let res = "";
            let name = "";
            let start = "";
            let end = "";
            for (let i in params) {
                let k = i % 2;
                if (!k) { //偶数
                   start = params[i].data.format('yyyy-MM-dd hh:mm:ss');
                }
                if (k) { //奇数
                    name = params[i].seriesName;
                    end = params[i].data.format('yyyy-MM-dd hh:mm:ss');;
                    res += name + " : " + end + "~" + start + "</br>";

                }
            }
            return res;
        }
    },
    series: series
}`;

var corChart=`let series =[];
let dataset = __dataset__;
for (let i=1;i<dataset[0].length;i++){
    series.push({type: 'bar',coordinateSystem: 'polar',stack: 'a'})
}
option__name__ = {
    angleAxis: {
        type: 'category',
        z: 10
    },
    radiusAxis:{},
    polar:{},
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            },
            position: function (pos, params, el, elRect, size) {
                var obj = {top: 10};
                obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 30;
                return obj;
            },
            extraCssText: 'width: 170px'
        },
    dataset: {source: dataset },
    series: series,
    legend: {}
}`;
var qrChart=`let dataset = __dataset__;
ds_loadjs('QRCode');
dom__name__.innerHTML = '';
let qrcode = new QRCode(dom__name__,{width:200, height:200});
qrcode.makeCode(dataset[1][0]);`;

var dlineChart=`let series = [];
let dataset = __dataset__;
let minVal = Infinity, maxVal = -Infinity;
for(let i=1; i<dataset.length; i++){
    for(let j=1; j<dataset[i].length; j++){
        minVal = Math.min(minVal, dataset[i][j]);
        maxVal = Math.max(maxVal, dataset[i][j]);
    }
}
const padding = (maxVal - minVal) * 0.2;
for(let i=1; i<dataset[0].length; i++){
    series.push({
        type: 'line',
        smooth: true,   
        symbol: 'circle',  
        symbolSize: 8,  
        lineStyle: {
            width: 3, 
            shadowColor: 'rgba(0,0,0,0.3)',
            shadowBlur: 8,
            shadowOffsetY: 6
        },
        areaStyle: { 
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                offset: 0,
                color: 'rgba(63, 129, 231, 0.8)'
            }, {
                offset: 1,
                color: 'rgba(63, 129, 231, 0.1)'
            }])
        }
    })
}

option__name__ = {
    legend: {},
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'cross'
        }
    },
    dataset: { source: dataset },
    xAxis: {
        type: 'category',
        axisLabel: {
            rotate: 45 
        }
    },
    yAxis: {
        type: 'value',
        min: Math.floor(minVal - padding),
        max: Math.ceil(maxVal + padding), 
        scale: true,
        splitLine: {
            show: true,
            lineStyle: {
                type: 'dashed'
            }
        }
    },
    series: series,
};`;