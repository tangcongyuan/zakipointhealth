// this is for plotting the line chart
var month = [];
var Cost_E = [];
var Cost_C = [];
var Cost_S = [];
var Cost_All = [];
$.ajax({
    url: 'http://cdqp.zakipoint.com/home/ajax_pmpm_data',
    success: function(data) {
	for(var object in JSON.parse(data['Pmpm_e'])['paidAmount']){
	    month.push(object);
	}
	
	//sort the month/year
	function MonthYearSort(a,b){
            months = {
                January:0,February:1,Mach:2,April:3,May:4,June:5,July:6,August:7,September:8,October:9,November:10,December:11};
            var as = a.split(' ');
            var bs = b.split(' ');
            var ad = new Date();
            var bd = new Date();
            ad.setMonth(months[as[0]]);
            ad.setYear(as[1]);
            bd.setMonth(months[bs[0]]);
            bd.setYear(bs[1]);
        return ad-bd;
        }
        
        month.sort(MonthYearSort);
	for(var object in month){
            Cost_E.push(Math.round(JSON.parse(data['Pmpm_e'])['paidAmount'][month[object]]));
            Cost_C.push(Math.round(JSON.parse(data['Pmpm_c'])['paidAmount'][month[object]]));
            Cost_S.push(Math.round(JSON.parse(data['Pmpm_s'])['paidAmount'][month[object]]));
            Cost_All.push(Math.round(JSON.parse(data['Pmpm_all'])['paidAmount'][month[object]]));         
        }
	
	$(function() {
         $('#PMPM').highcharts({
        title: {
            text: 'PMPM',
            x: -20 //center
        },
        xAxis: {
            categories: month
        },
        yAxis: {
            title: {
                text: 'Average Cost ($)'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
	tooltip: {
            valueSuffix: '$',
        
        crosshairs:[{
            width:1,
            color:"#006cee",
            dashStyle:'longdashdot',
            xIndex:100
        },{
            width:1,
            color:"#006cee",
            dashSyle:'longdashdot',
            xIndex:100
        }]
        },
	legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle',
            borderWidth: 0
        },
	 series: [
                {
            name: 'Employee',
            data:Cost_E},
                {
            name: 'Child',
            data:Cost_C},
                {
            name: 'Spouse',
            data:Cost_S},
                {
            name: 'All',
            data:Cost_All}
                ],
        credits:{
                enabled:false
                },
    });
});

    },
    failure: function(data) { 
        alert('Got an error dude');
    }
});


//this is to plot the bubble chart

var cost = [];
var avgQual = [];
var providerName = [];

$.ajax({
    url: 'http://cdqp.zakipoint.com/home/ajax_strategy_data',
    success: function(data) {
	for(var i =0;i<JSON.parse(data).length;i++){
		cost.push(JSON.parse(data)[i]['cost']);
		avgQual.push(JSON.parse(data)[i]['avgQual']);
		providerName.push(JSON.parse(data)[i]['providerName']);
	}
	
	var serieslist = [];
	for(var i =0;i<providerName.length;i++){
		var object ={
		name:providerName[i],
		data:[cost[i],avgQual[i],cost[i]]};
		serieslist.push(object);
	}
	$(function(){
	$('#bubblechart').highcharts({
	
	    chart:{
		type:'bubble',
		zoomType:'xy'
		},
	
	    title:{
		text:'Narrow Network Plan'
		},
	
	   //series:serieslist
	    
	});
	});
    },
    failure: function(data) {
        alert('Got an error dude');
    }
});
