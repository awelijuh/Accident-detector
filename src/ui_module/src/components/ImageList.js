import React, {useEffect, useState} from "react";
import {Container} from "react-bootstrap-v5";
import Viewer from "react-viewer";
import {useInView} from "react-intersection-observer";
import logo from "../logo.svg";
import {DATA_URL} from "./const";
import {getDateFormatFromFileName} from "./Utils";

function Item({image, onClick}) {

    const {ref, inView, entry} = useInView({
        /* Optional options */
        threshold: 0,
    });


    return (
        <div ref={ref} className="d-inline-block m-2 border"
             style={{cursor: 'pointer', width: '300px', height: '200px', minWidth: '300px', minHeight: '200px'}}
             onClick={onClick}>
            <img src={inView ? image.src : logo} style={{width: '300px', height: '200px'}} alt={image?.alt}/>
            <div className="text-center">{image.caption}</div>
        </div>
    )

}

function getImageObjects(files) {
    let d = []
    for (let index in files) {
        d.push({
            src: DATA_URL + 'media/' + files[index],
            caption: getDateFormatFromFileName(files[index]),
            alt: getDateFormatFromFileName(files[index]),
        })
    }
    return d
}

function ImageList(props) {

    const [files, setFiles] = useState()

    const [showImage, setShowImage] = useState(false);
    const [currentImageIndex, setCurrentImageIndex] = useState(0);

    function fetchFiles() {
        fetch('http://localhost:5000/list').then();
        // if (!resp.ok) {
        //     return
        // }
        // let d = await resp.json()
        // setFiles(getImageObjects(d))
    }

    useEffect(() => {
        fetchFiles()
        console.log('useEffect')
    }, [props])

    function onImageSelect(index) {
        setCurrentImageIndex(index)
        setShowImage(true)
    }

    return (
        <Container className="text-center">
            {files?.map?.((value, index) => <Item key={index} image={value} onClick={() => onImageSelect(index)}/>)}
            <Viewer
                visible={showImage}
                onClose={() => setShowImage(false)}
                images={files}
                activeIndex={currentImageIndex}
                onChange={(dec, n) => setCurrentImageIndex(n)}
                noNavbar
                loop={false}
            />

        </Container>
    );

}

export default ImageList
