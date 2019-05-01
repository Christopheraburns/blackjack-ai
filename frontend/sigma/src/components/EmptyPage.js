import React, {Component} from 'react';
import {Button} from 'primereact/button';
import Amplify, { PubSub } from 'aws-amplify';
import { AWSIoTProvider } from '@aws-amplify/pubsub/lib/Providers';

// Amplify.addPluggable(new AWSIoTProvider({
//     aws_pubsub_region: 'us-east-1',
//     aws_pubsub_endpoint: 'wss://a24uoola4timn8-ats.iot.us-east-1.amazonaws.com/mqtt'
// }));

export class EmptyPage extends Component {

    constructor() {
        super();
        this.state = {
            subscription: null,
            img1 : "transparentPix.png"
        };
    }

    connect = () => {
        this.setState({
            subscription: PubSub.subscribe('newimages').subscribe({
                next: data => this.setState({
                    img1 : data.value.s3Key
                }),
                error: error => console.error(error),
                close: () => console.log('Done'),
            })
        });
    }

    // old
    // connect = () => {
    //     this.setState({
    //         subscription: PubSub.subscribe('helloworld').subscribe({
    //             next: data => this.setState({
    //                 info: data.value.msg
    //             }),
    //             error: error => console.error(error),
    //             close: () => console.log('Done'),
    //         })
    //     });
    // }

    submit = () => {
        PubSub.publish('takeimage', { msg: 'helloworld' });
        console.log('hello');
    }

    unsub = () => {
        this.state.subscription.unsubscribe();
    }

    render() {

        return (
            <div className="p-grid">
                <div className="p-col-12">
                    <div className="card">
                        <h1>Pub</h1>
                        <div className="p-col-6 p-md-4">
                                    <Button label="Send IoT Message" icon="pi pi-external-link" onClick={this.submit} />
                        </div>
                    </div>
                    <div className="card">
                        <h1>Sub</h1>
                        <div className="p-col-12 p-md-4">
                            <Button label="Show Messages" icon="pi pi-external-link" onClick={this.connect} />
                            <p>
                            <img src={"https://dkszktluuqk1z.cloudfront.net/" + this.state.img1} alt='python' width="300" height="300"/>
                            </p>
                        </div>
                    </div>
                    <div className="card">
                        <h1>UnSub</h1>
                        <div className="p-col-12 p-md-4">
                                    <Button label="Show Messages" icon="pi pi-external-link" onClick={this.unsub} />
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}