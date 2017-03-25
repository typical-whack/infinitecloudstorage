import React from 'react';
import { Button, Col, Grid, Jumbotron, PageHeader, Row} from 'react-bootstrap';
import FileUploadProgress from 'react-fileupload-progress';
import ReactDOM from 'react-dom';
import api from './api.js';

const FilePage = React.createClass({
    getInitialState() {
        return {
            files: [{
                file_name: 'Test Name',
                file_size: '101010101',
                last_modified: '01/01/01',
                id: '101091i201293123'
            }],
            loading: 'Files Loading'
        };
    },

    componentWillMount: function() {
        this.fetchFiles();
    },

    uploadFile: function(event) {
        event.preventDefault();
        const file = document.getElementById('fileUpload').files[0];
        console.log(file);
        const success = () => {
            console.log('Success');
        };
        const error = (results) => {
            console.log(results);
        };
        api.uploadFile(file, success, error);
    },

    fetchFiles: function() {
        const success = (results) => {
            this.setState({
                loading: 'No Files'
            })
            // this.setState({
            //     files: results.files
            // });
        };
        const error = (results) => {
            this.setState({
                loading: 'Error getting files'
            });
        };
        api.getFiles(success, error);
    },

    renderUpload: function(onSubmit){
        return (
            <div style={{align: 'left', width: '170px'}}>
                <p style={{textAlign: 'center'}}>Upload File</p>
                <form id='customForm' style={{marginBottom: '15px'}}>
                    <input type='file' type='file' name='file' id='fileUpload'/>
                    <div >
                        <Button type='button' style={styles.bsButton} onClick={onSubmit}>Upload</Button>
                    </div>
                </form>
            </div>
        );
    },

    renderProgress(progress, hasError, cancelHandler) {
        if (hasError || progress > -1 ) {
            let barStyle = Object.assign({}, styles.progressBar);
            barStyle.width = progress + '%';

            let message = (<span>{barStyle.width}</span>);
            if (hasError) {
                barStyle.backgroundColor = '#d9534f';
                message = (<span >Failed to upload ...</span>);
            }
            else if (progress === 100){
                message = (<span >Done</span>);
            }
            return (
                <div>
                    <div style={styles.progressWrapper}>
                        <div style={barStyle}></div>
                    </div>
                    <button style={styles.cancelButton} onClick={cancelHandler}>
                        <span>&times;</span>
                    </button>
                    <div style={{'clear':'left'}}>
                        {message}
                    </div>
                </div>
            );
        } else {
            return;
        }
    },

    formGetter(){
        return new FormData(document.getElementById('customForm'));
    },

    renderTable: function () {
        return (
            <div key='files'>
                <table className='table table-striped table-condensed'>
                    <thead>
                        <tr>
                            <th>File Name</th>
                            <th>File Size</th>
                            <th>Date Last Modified</th>
                            <th>Remove</th>
                        </tr>
                    </thead>
                    <tbody>
                    {this.state.files.map(this.renderFile)}
                    </tbody>
                </table>
            </div>
        );
    },

    removeFromList: function(id) {
        const tempList = this.state.files;
        tempList.forEach(function(e, index) {
            if (e.id === id) {
                tempList.splice(index);
            }
        }, this);
        this.setState({
            files: tempList
        });
    },

    removeFile: function(event) {
        const success = (results) => {
            //this.removeFromList(results.id);
        };
        const error = (results) => {
            this.setState({
                error: 'Failed to remove file'
            });
        };
        api.deleteFile(event.target.id, success, error);
    },

    getFile: function(event) {
        const success = (results) => {
            //this.removeFromList(results.id);
        };
        const error = (results) => {
            this.setState({
                error: 'Failed to download file'
            });
        };
        api.getFile(event.target.id, event.target.text, success, error);
    },

    renderFile: function(f) {
        return (
            <tr key={'file:' + f.id}>
                <td>
                    <a id={f.id} style={{cursor:'pointer'}} onClick={this.getFile}>
                        {f.file_name}
                    </a>
                </td>
                <td> {f.file_size} </td>
                <td> {f.last_modified} </td>
                <td>
                    <a id={f.id} style={{cursor:'pointer'}} onClick={this.removeFile}>
                        Remove
                    </a>
                </td>
            </tr>
         );
    },

    render: function() {
        return (
            <Jumbotron>
                <PageHeader className='container'>Infinite Cloud Storage!</PageHeader>
                <div className='container'>

                    <FileUploadProgress key='ex2' url='http://localhost:5000/upload_file'
                        onProgress={(e, request, progress) => {console.log('progress', e, request, progress);}}
                        onLoad={ (e, request) => {console.log('load', e, request);}}
                        onError={ (e, request) => {console.log('error', e, request);}}
                        onAbort={ (e, request) => {console.log('abort', e, request);}}
                        formGetter={this.formGetter}
                        formRenderer={this.renderUpload}
                        progressRenderer={this.renderProgress}
                        />
                </div>
                {this.state.files.length
                    ? <div className='container'>
                        {this.renderTable()}
                    </div>
                    : <div className='container'>
                        <p> {this.state.loading} </p>
                    </div>
                }
            </Jumbotron>
        );
    }
});

const styles = {
    progressWrapper: {
        height: '50px',
        marginTop: '10px',
        width: '400px',
        float:'left',
        overflow: 'hidden',
        backgroundColor: '#f5f5f5',
        borderRadius: '4px',
        WebkitBoxShadow: 'inset 0 1px 2px rgba(0,0,0,.1)',
        boxShadow: 'inset 0 1px 2px rgba(0,0,0,.1)'
    },
    progressBar: {
        float: 'left',
        width: '0',
        height: '100%',
        fontSize: '12px',
        lineHeight: '20px',
        color: '#fff',
        textAlign: 'center',
        backgroundColor: '#5cb85c',
        WebkitBoxShadow: 'inset 0 -1px 0 rgba(0,0,0,.15)',
        boxShadow: 'inset 0 -1px 0 rgba(0,0,0,.15)',
        WebkitTransition: 'width .6s ease',
        Otransition: 'width .6s ease',
        transition: 'width .6s ease'
    },
    cancelButton: {
        marginTop: '5px',
        WebkitAppearance: 'none',
        padding: 0,
        cursor: 'pointer',
        background: '0 0',
        border: 0,
        float: 'left',
        fontSize: '21px',
        fontWeight: 700,
        lineHeight: 1,
        color: '#000',
        textShadow: '0 1px 0 #fff',
        filter: 'alpha(opacity=20)',
        opacity: '.2'
    },

    bsButton: {
        marginRight: 'auto',
        marginLeft: 'auto',
        display: 'inline',
        marginTop: '15px',
        fontSize: '12px',
        lineHeight: '1.5',
        borderRadius: '3px',
        color: '#fff',
        backgroundColor: '#337ab7',
        borderColor: '#2e6da4',
        display: 'block',
        fontWeight: 400,
        textAlign: 'center',
        whiteSpace: 'nowrap',
        verticalAlign: 'middle',
        touchAction: 'manipulation',
        cursor: 'pointer',
        userSelect: 'none',
        backgroundImage: 'none',
        border: '1px solid transparent'
    },
};


export default FilePage;
