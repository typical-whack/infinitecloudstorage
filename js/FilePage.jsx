import React from 'react';
import { Button, Col, Grid, Jumbotron, PageHeader, Row} from 'react-bootstrap';
import FileUploadProgress from 'react-fileupload-progress';
import ReactDOM from 'react-dom';
import api from './api.js';

const FilePage = React.createClass({
    getInitialState() {
        return {
            files: [],
            loading: 'Files Loading'
        };
    },

    componentWillMount: function() {
        this.fetchFiles();
    },

    fetchFiles: function() {
        const success = (results) => {
            this.setState({
                loading: 'No Files',
                files: results.data
            })
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
        return;
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
                            <th>File Size (In Bytes)</th>
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
            if (e.file_id === id) {
                tempList.splice(index);
            }
        }, this);
        this.setState({
            files: tempList
        });
    },

    removeFile: function(event) {
        const success = (results) => {
            this.removeFromList(results.data);
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
        const link = window.location.protocol + '//' + window.location.host + '/get_file/';
        return (
            <tr key={'file:' + f.file_id}>
                <td>
                    <a style={{cursor:'pointer'}} href={link+f.file_id + '/' + f.file_name}>
                        {f.file_name}
                    </a>
                </td>
                <td> {f.size} </td>
                <td> {f.date} </td>
                <td>
                    <a id={f.file_id} style={{cursor:'pointer'}} onClick={this.removeFile}>
                        Remove
                    </a>
                </td>
            </tr>
         );
    },

    addFile: function(file_list) {
        const file = {
            'file_id': file_list[0],
            'file_name': file_list[1],
            'size': file_list[2],
            'date': file_list[3]
        }
        this.setState({
            files: this.state.files.concat(file)
        });
    },

    render: function() {
        return (
            <div>
                <PageHeader className='container'>Infinite Cloud Storage!</PageHeader>
                <div className='container'>

                    <FileUploadProgress key='ex2' url='http://localhost:5000/upload_file'
                        onLoad={ (e, request) => {
                            const file_list = JSON.parse(e.target.response).data;
                            this.addFile(file_list);
                        }}
                        onError={ (e, request) => {console.log('error');}}
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
            </div>
        );
    }
});

const styles = {
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
