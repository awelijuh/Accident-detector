import "bootstrap/dist/css/bootstrap.min.css"
// import 'bootstrap/scss/bootstrap.scss'
import {Nav, Navbar} from "react-bootstrap-v5";
import React, {useState} from "react";
import "./styles.css"
import {DATA_URL} from "../const";
import {VideoView} from "./Stream/VideoView";
import {Info} from "./Stream/Info"
import {VideoTable} from "./video_table";
import {BrowserRouter, Link, Route, Routes} from "react-router-dom";
import DataList from "./Data/DataList";

function App(props) {
    const [page, setPage] = useState(1)
    const [options, setOptions] = useState({size: '480', type: 'detected'})

    return (
        <div>
            <Navbar bg="secondary" variant="dark" className="mb-1">
                <div onClick={() => setPage(0)} className="navbar-brand"></div>
                <Nav className="mr-auto">
                    <Link to={"/accidents"} className="nav-link cursor-pointer">Записи</Link>
                    <Link to={"/stream"} className="nav-link cursor-pointer">Стрим</Link>
                    <Link to={"/data"} className="nav-link cursor-pointer">Данные</Link>
                </Nav>
            </Navbar>
            <div className="d-flex mt-2">
                <>
                    <Routes>
                        <Route
                            path="/"
                            element={<VideoTable/>}
                        />
                        <Route
                            path="accidents"
                            element={<VideoTable/>}
                        />
                        <Route
                            path="stream"
                            element={<VideoView/>}
                        />
                        <Route
                            path="data"
                            element={<DataList/>}
                        />

                    </Routes>

                </>
            </div>

        </div>
    )
}

export default App;
