import React, {forwardRef, useEffect, useState} from "react";
import {DATA_URL} from "../../const";
import moment from "moment";
import {Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis} from "recharts";
import {
    Container,
    FormControl,
    IconButton,
    InputLabel,
    LinearProgress,
    MenuItem,
    Paper,
    Select,
    TextField
} from "@mui/material";
import {
    AddBox, ArrowDownward,
    Check, ChevronLeft,
    ChevronRight,
    Clear,
    DeleteOutline,
    Edit,
    FilterList,
    FirstPage, LastPage, Refresh, Remove,
    SaveAlt, Search, ViewColumn
} from "@mui/icons-material";
import MaterialTable from "@material-table/core";
import Filter from "./Filter";

const average = array => array == null || array.length === 0 ? undefined : array.reduce((a, b) => a + b) / array.length;

function median(values) {
    if (values.length === 0) return undefined;

    values.sort(function (a, b) {
        return a - b;
    });

    var half = Math.floor(values.length / 2);

    if (values.length % 2)
        return values[half];

    return (values[half - 1] + values[half]) / 2.0;
}


const tableIcons = {
    Add: forwardRef((props, ref) => <AddBox {...props} ref={ref}/>),
    Check: forwardRef((props, ref) => <Check {...props} ref={ref}/>),
    Clear: forwardRef((props, ref) => <Clear {...props} ref={ref}/>),
    Delete: forwardRef((props, ref) => <DeleteOutline {...props} ref={ref}/>),
    DetailPanel: forwardRef((props, ref) => <ChevronRight {...props} ref={ref}/>),
    Edit: forwardRef((props, ref) => <Edit {...props} ref={ref}/>),
    Export: forwardRef((props, ref) => <SaveAlt {...props} ref={ref}/>),
    Filter: forwardRef((props, ref) => <FilterList {...props} ref={ref}/>),
    FirstPage: forwardRef((props, ref) => <FirstPage {...props} ref={ref}/>),
    LastPage: forwardRef((props, ref) => <LastPage {...props} ref={ref}/>),
    NextPage: forwardRef((props, ref) => <ChevronRight {...props} ref={ref}/>),
    PreviousPage: forwardRef((props, ref) => <ChevronLeft {...props} ref={ref}/>),
    ResetSearch: forwardRef((props, ref) => <Clear {...props} ref={ref}/>),
    Search: forwardRef((props, ref) => <Search {...props} ref={ref}/>),
    SortArrow: forwardRef((props, ref) => <ArrowDownward {...props} ref={ref}/>),
    ThirdStateCheck: forwardRef((props, ref) => <Remove {...props} ref={ref}/>),
    ViewColumn: forwardRef((props, ref) => <ViewColumn {...props} ref={ref}/>)
};


function DataTable({data}) {


    return (

        <MaterialTable options={{padding: "dense"}} title={"Данные"} icons={tableIcons} columns={[
            {
                title: 'Время',
                render: row => (
                    <span
                        title={moment(Date.parse(row.time)).format("DD.MM.YYYY HH:mm:ss")}>
                            {moment(Date.parse(row.time)).format("HH:mm:ss.SSS")}
                        </span>)
            },
            {title: 'Машины', field: 'car'},
            {title: 'Грузовики', field: 'truck'},
            {title: 'Автобусы', field: 'bus'},
            // {title: 'Люди', field: 'person'},
            {title: 'Все', field: 'all'},
            // {title: 'Фото', field: 'image'},
        ]} data={data}/>

    )
}


function DataChart({data}) {
    console.log(data)
    return (
        <ResponsiveContainer width='100%' height={400}>
            <BarChart height={400} data={data}>
                <XAxis dataKey="delta"/>
                <YAxis yAxisId="a"/>
                <YAxis yAxisId="b" orientation="right"/>
                <Legend/>
                <Tooltip/>
                <CartesianGrid vertical={false}/>
                <Bar fill="#00CCFF" yAxisId="a" dataKey="count">
                </Bar>

            </BarChart>
        </ResponsiveContainer>
    )
}

function getDefaultStartTime() {
    let time = new Date();
    time.setHours(0)
    time.setMinutes(0)
    time.setSeconds(0)
    time.setMilliseconds(0)

    return moment(time).format("YYYY-MM-DDTHH:mm")
}

function getDefaultEndTime() {
    let time = new Date();
    time.setHours(0)
    time.setMinutes(0)
    time.setSeconds(0)
    time.setMilliseconds(0)
    time = moment(time).add(1, 'day')

    return time.format("YYYY-MM-DDTHH:mm")
}

function DataList(props) {
    console.log(getDefaultStartTime())
    console.log(getDefaultEndTime())
    const [data, setData] = useState()
    const [numData, setNumData] = useState()
    const [loading, setLoading] = useState(true)

    const [filter, setFilter] = useState({
        classes: [],
        start_time: getDefaultStartTime(),
        end_time: getDefaultEndTime(),
        aggregate: 'average',
    })


    function getUrl() {
        let url = new URL(DATA_URL + "filterObjects")
        let f = {...filter}
        f.start_time = new Date(f.start_time).toISOString().replace('Z', '')
        f.end_time = new Date(f.end_time).toISOString().replace('Z', '')
        url.search = new URLSearchParams(f).toString();
        return url;
    }

    async function fetchTableData(arrayLike) {
        setLoading(true)
        let url = getUrl().toString()
        let resp = await fetch(url)
        if (!resp.ok) {
            setLoading(false)
            return
        }
        let d = await resp.json()

        if (url.toString() !== getUrl().toString()) {
            console.log('not equal')
            return
        }

        let nd = {}

        console.log('d', d)

        let keys = []
        for (let x in d) {
            keys.push(d[x].delta)
            let t = Math.round(d[x].delta)
            if (nd[t] == null) {
                nd[t] = 0
            }
            nd[t]++;
        }

        console.log('keys', keys)

        let nmData = {
            min: Math.min(...keys),
            max: Math.max(...keys),
            average: average(keys),
            median: median(keys),
            count: keys.length
        }

        console.log('numData', nmData)

        let result = []

        for (let i in nd) {
            result.push({
                delta: i,
                count: nd[i]
            })
        }

        setData(result)
        setNumData(nmData)

        setLoading(false)
    }

    useEffect(() => {
        fetchTableData()
    }, [filter])

    console.log(numData)

    return (
        <Container>
            <Paper className="p-3 m-2">
                <Filter value={filter} onChange={v => setFilter(v)} onUpdate={() => fetchTableData()}/>
            </Paper>

            {
                loading
                    ? <LinearProgress className="m-2"/>
                    : <></>
            }
            <ul>
                {

                    numData != null ? Object.keys(numData)?.map?.((key) =>
                            <li key={numData[key]}><b>{key}:</b> {numData[key]}</li>
                        )
                        : <></>
                }
            </ul>
            <Paper className="p-3 m-2">
                <DataChart data={data}/>
            </Paper>

        </Container>

    )
}

export default DataList
