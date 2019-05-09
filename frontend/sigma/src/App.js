import React, {Component} from 'react';
import {Panel} from 'primereact/panel';
import {Dialog} from 'primereact/dialog';
import classNames from 'classnames';
import {AppTopbar} from './AppTopbar';
import {Button} from 'primereact/button';
import {AppFooter} from './AppFooter';
import {AppMenu} from './AppMenu';
import {AppInlineProfile} from './AppInlineProfile';
import {Route} from 'react-router-dom';
import {Dashboard} from './components/Dashboard';
import {FormsDemo} from './components/FormsDemo';
import {SampleDemo} from './components/SampleDemo';
import {DataDemo} from './components/DataDemo';
import {PanelsDemo} from './components/PanelsDemo';
import {OverlaysDemo} from './components/OverlaysDemo';
import {MenusDemo} from './components/MenusDemo';
import {MessagesDemo} from './components/MessagesDemo';
import {ChartsDemo} from './components/ChartsDemo';
import {MiscDemo} from './components/MiscDemo';
import {EmptyPage} from './components/EmptyPage';
import {Documentation} from "./components/Documentation";
import {ScrollPanel} from 'primereact/components/scrollpanel/ScrollPanel';
import 'primereact/resources/themes/nova-light/theme.css';
import 'primereact/resources/primereact.min.css';
import 'primeicons/primeicons.css';
import 'primeflex/primeflex.css';
import 'fullcalendar/dist/fullcalendar.css';
import './layout/layout.css';
import './App.css';
import {Chart} from 'primereact/chart';
import Amplify, { PubSub, API } from 'aws-amplify';
import { AWSIoTProvider } from '@aws-amplify/pubsub/lib/Providers';

import awsmobile from './aws-exports';
import { ConfirmSignIn, SignIn, withAuthenticator, Greetings, SignOut } from 'aws-amplify-react';
import { SignUp } from 'aws-amplify-react/dist/Auth';

Amplify.configure(awsmobile);

Amplify.addPluggable(new AWSIoTProvider({
    aws_pubsub_region: 'us-east-1',
    aws_pubsub_endpoint: 'wss://a24uoola4timn8-ats.iot.us-east-1.amazonaws.com/mqtt'
}));

Amplify.configure({
    Auth: {
        // REQUIRED - Amazon Cognito Identity Pool ID
        identityPoolId: 'us-east-1:e48cc2f0-641c-485a-9521-2cf7899f6cd1',
        // REQUIRED - Amazon Cognito Region
        region: 'us-east-1', 
        // OPTIONAL - Amazon Cognito User Pool ID
        userPoolId: 'us-east-1_0Ig7HkLsf'
    },
    API: {
        endpoints: [
            {
                name: "MyLambdaAPI",
                endpoint: "https://urbpvus9rd.execute-api.us-east-1.amazonaws.com"
            }
        ]
    }
  });

let apiName = 'MyLambdaAPI';
let path = '/dev';
let myInit = { // OPTIONAL
  body: {}
}

class App extends Component {
    
        constructor() {
            super();
            this.state = {
                probabilities: [
                    30.8,
                    7.7,
                    7.7,
                    7.7,
                    7.7,
                    7.7,
                    7.7,
                    7.7,
                    7.7,
                    7.7
                ],
                countsdata: [
                    64,
                    16,
                    16,
                    16,
                    16,
                    16,
                    16,
                    16,
                    16,
                    16
                ],
                pl1imgsub: PubSub.subscribe('newimagespl1').subscribe({
                    next: data => this.setState({
                        img1 : data.value.s3Key
                    }),
                    error: error => console.error(error),
                    close: () => console.log('Done'),
                }),
                pl2imgsub: PubSub.subscribe('newimagespl2').subscribe({
                    next: data => this.setState({
                        img2 : data.value.s3Key
                    }),
                    error: error => console.error(error),
                    close: () => console.log('Done'),
                }),
                pl3imgsub: PubSub.subscribe('newimagespl3').subscribe({
                    next: data => this.setState({
                        img3 : data.value.s3Key
                    }),
                    error: error => console.error(error),
                    close: () => console.log('Done'),
                }),
                pl4imgsub: PubSub.subscribe('newimagespl4').subscribe({
                    next: data => this.setState({
                        img4 : data.value.s3Key
                    }),
                    error: error => console.error(error),
                    close: () => console.log('Done'),
                }),
                pl5imgsub: PubSub.subscribe('newimagespl5').subscribe({
                    next: data => this.setState({
                        img5 : data.value.s3Key
                    }),
                    error: error => console.error(error),
                    close: () => console.log('Done'),
                }),
                dlrimgsub: PubSub.subscribe('newimagesdlr').subscribe({
                    next: data => this.setState({
                        img6 : data.value.s3Key
                    }),
                    error: error => console.error(error),
                    close: () => console.log('Done'),
                }),
                pl1guidancesub: PubSub.subscribe('guidancepl1').subscribe({
                    next: data => this.setState({
                        pl1guidance : data.value.guidance
                    }),
                    error: error => console.error(error),
                    close: () => console.log('Done'),
                }),
                pl2guidancesub: PubSub.subscribe('guidancepl2').subscribe({
                    next: data => this.setState({
                        pl2guidance : data.value.guidance
                    }),
                    error: error => console.error(error),
                    close: () => console.log('Done'),
                }),
                pl3guidancesub: PubSub.subscribe('guidancepl3').subscribe({
                    next: data => this.setState({
                        pl3guidance : data.value.guidance
                    }),
                    error: error => console.error(error),
                    close: () => console.log('Done'),
                }),
                pl4guidancesub: PubSub.subscribe('guidancepl4').subscribe({
                    next: data => this.setState({
                        pl4guidance : data.value.guidance
                    }),
                    error: error => console.error(error),
                    close: () => console.log('Done'),
                }),
                pl5guidancesub: PubSub.subscribe('guidancepl5').subscribe({
                    next: data => this.setState({
                        pl5guidance : data.value.guidance
                    }),
                    error: error => console.error(error),
                    close: () => console.log('Done'),
                }),
                countssub: PubSub.subscribe('counts').subscribe({
                    next: data => this.setState({
                        countsdata : data.value
                    }),
                    error: error => console.error(error),
                    close: () => console.log('Done'),
                }),
                probabilitiessub: PubSub.subscribe('probabilities').subscribe({
                    next: data => this.setState({
                        probabilities : data.value
                    }),
                    error: error => console.error(error),
                    close: () => console.log('Done'),
                }),
                img1 : "transparentPix.png",
                img2 : "transparentPix.png",
                img3 : "transparentPix.png",
                img4 : "transparentPix.png",
                img5 : "transparentPix.png",
                img6 : "transparentPix.png",
                reset_visible: false,
                shuffle_visible: false

                
            };
            this.onResetClick = this.onResetClick.bind(this);
            this.onResetHideYes = this.onResetHideYes.bind(this);
            this.onResetHideNo = this.onResetHideNo.bind(this);
            this.onShuffleClick = this.onShuffleClick.bind(this);
            this.onShuffleHideYes = this.onShuffleHideYes.bind(this);
            this.onShuffleHideNo = this.onShuffleHideNo.bind(this);
        }

        postShoeReset() {
            myInit.body.arg = "shuffle"
            API.post(apiName, path, myInit).then(response => {
              this.setState({
                itemData: response.data
              });
            });
            this.setState({
                countsdata: [
                    64,
                    16,
                    16,
                    16,
                    16,
                    16,
                    16,
                    16,
                    16,
                    16,
                    16,
                    16,
                    16
                ],
                probabilities: [
                    30.8,
                    7.7,
                    7.7,
                    7.7,
                    7.7,
                    7.7,
                    7.7,
                    7.7,
                    7.7,
                    7.7,
                    7.7,
                    7.7,
                    7.7
                ]
            })
          }

        postDedupReset() {
            myInit.body.arg = "new_round"
            API.post(apiName, path, myInit).then(response => {
              this.setState({
                itemData: response.data
              });
            });
        }

        onResetClick(event) {
            this.setState({reset_visible: true});
        }

        onResetHideYes(event) {
            this.postDedupReset();
            this.setState({reset_visible: false});
        }

        onResetHideNo(event) {
            this.setState({reset_visible: false});
        }

        onShuffleClick(event) {
            this.setState({shuffle_visible: true});
        }

        onShuffleHideYes(event) {
            this.postShoeReset();
            this.setState({shuffle_visible: false});
        }

        onShuffleHideNo(event) {
            this.setState({shuffle_visible: false});
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
    
        submit = () => {
            PubSub.publish('takeimage', { msg: 'helloworld' });
            console.log('hello');
        }
    
        unsub = () => {
            this.state.subscription.unsubscribe();
        }
    
        render() {
            const shuffle_footer = (
                <div>
                    <Button style={{textAlign: "center", background: "#fd4f00", color:"#ffffff", border: "#fd4f00"}} label="Yes" onClick={this.onShuffleHideYes} />
                    <Button style={{textAlign: "center", background: "#a7a9ac", color:"#ffffff" }} label="No" onClick={this.onShuffleHideNo} className="p-button-secondary" />
                </div>
            );

            const reset_footer = (
                <div>
                    <Button style={{textAlign: "center", background: "#fd4f00", color:"#ffffff", border: "#fd4f00"}} label="Yes" onClick={this.onResetHideYes} />
                    <Button style={{textAlign: "center", background: "#a7a9ac", color:"#ffffff" }} label="No" onClick={this.onResetHideNo} className="p-button-secondary" />
                </div>
            );

            let chartdata = {
                labels: ['Cards Worth 10', 'Ace', 'Nine', 'Eight', 'Seven', 'Six', 'Five', 'Four', 'Three', 'Two'],
                datasets: [
                    {
                        type: 'line',
                        label: 'Probabilities',
                        borderColor: '#3c3533',
                        yAxisID: 'y-axis-1',
                        borderWidth: 2,
                        fill: true,
                        data: this.state.probabilities
                    },
                    {
                        type: 'bar',
                        label: 'Counts',
                        backgroundColor: '#b5be00',
                        yAxisID: 'y-axis-1',
                        fill: true,
                        data: this.state.countsdata
                    }
                ]
            };
      
            const multiAxisOptions = {
                responsive: true,
                tooltips: {
                  mode: 'index',
                  intersect: true
                },
                scales: {
                  yAxes: [
                    {
                      type: 'linear',
                      display: true,
                      position: 'left',
                      id: 'y-axis-1'
                    }
                  ]
                }
              };
    
            return (
                <div className="p-grid p-fluid">
                    <Dialog header="Confirm" visible={this.state.shuffle_visible} style={{width: '50vw'}} footer={shuffle_footer} onHide={this.onShuffleHideNo} maximizable>
                        Are you sure you want to reset the shoe count?
                    </Dialog>
                    <Dialog header="Confirm" visible={this.state.reset_visible} style={{width: '50vw'}} footer={reset_footer} onHide={this.onResetHideNo} maximizable>
                        Are you sure you are starting a new round and you are ready to clear the dedup table?
                    </Dialog>

                    <div className="p-col-12 p-lg-12">
                        <div className="card" style={{textAlign: "center", background: "#fd4f00", color:"#ffffff" }}>
                            <h1>re:Vegas Challenge</h1>
                        </div>
                    </div>
                    <div className="p-col-12 p-lg-6">
                        <div className="card">
                            <h1 style={{fontSize:'16px'}}>New Round</h1>
                            <Button style={{background: '#25cbd2', border: '#25cbd2'}} label="New Round" icon="pi pi-external-link" onClick={this.onResetClick}/>
                        </div>
                    </div>
                    <div className="p-col-12 p-lg-6">
                        <div className="card">
                            <h1 style={{fontSize:'16px'}}>Deck Shuffle</h1>
                            <Button style={{background: '#25cbd2', border: '#25cbd2'}} label="Clear Counts" icon="pi pi-external-link" onClick={this.onShuffleClick}/>
                        </div>
                    </div>
                    <div className="p-col-12 p-md-6 p-lg-4">
                        <Panel header="Player 1" style={{height: '100%'}}>
                            <p>
                                <img style={{height: "auto", maxWidth: "100%", marginLeft: "auto", marginRight:"auto", display: "block"}} src={"https://dkszktluuqk1z.cloudfront.net/" + this.state.img1} alt='pix' />
                                <p style={{fontSize: 
                                "20px", textAlign: "center", color: "#FFFFFF", backgroundColor: "#25cbd3"}}>{this.state.pl1guidance}</p>
                            </p>
                        </Panel>
                    </div>
                    <div className="p-col-12 p-md-6 p-lg-4">
                        <Panel header="Player 2" style={{height: '100%'}}>
                        <p>
                                <img style={{height: "auto", maxWidth: "100%", marginLeft: "auto", marginRight:"auto", display: "block"}} src={"https://dkszktluuqk1z.cloudfront.net/" + this.state.img2} alt='pix' />
                                <p style={{fontSize: 
                                "20px", textAlign: "center", color: "#FFFFFF", backgroundColor: "#25cbd3"}}>{this.state.pl2guidance}</p>
                        </p>
                        </Panel>
                    </div>
                    <div className="p-col-12 p-md-6 p-lg-4">
                        <Panel header="Player 3" style={{height: '100%'}}>
                        <p>
                                <img style={{height: "auto", maxWidth: "100%", marginLeft: "auto", marginRight:"auto", display: "block"}} src={"https://dkszktluuqk1z.cloudfront.net/" + this.state.img3} alt='pix' />
                                <p style={{fontSize: 
                                "20px", textAlign: "center", color: "#FFFFFF", backgroundColor: "#25cbd3"}}>{this.state.pl3guidance}</p>
                        </p>
                        </Panel>
                    </div>
                    <div className="p-col-12 p-md-6 p-lg-4">
                        <Panel header="Player 4" style={{height: '100%'}}>
                        <p>
                                <img style={{height: "auto", maxWidth: "100%", marginLeft: "auto", marginRight:"auto", display: "block"}} src={"https://dkszktluuqk1z.cloudfront.net/" + this.state.img4} alt='pix' />
                                <p style={{fontSize: 
                                "20px", textAlign: "center", color: "#FFFFFF", backgroundColor: "#25cbd3"}}>{this.state.pl4guidance}</p>
                        </p>
                        </Panel>
                    </div>
                    <div className="p-col-12 p-md-6 p-lg-4">
                        <Panel header="Player 5" style={{height: '100%'}}>
                            <p>
                                    <img style={{height: "auto", maxWidth: "100%", marginLeft: "auto", marginRight:"auto", display: "block"}} src={"https://dkszktluuqk1z.cloudfront.net/" + this.state.img5} alt='pix'/>
                            </p>
                            <p style={{fontSize: 
                                "20px", textAlign: "center", color: "#FFFFFF", backgroundColor: "#25cbd3"}}>{this.state.pl5guidance}</p>
                        </Panel>
                    </div>
                    <div className="p-col-12 p-md-6 p-lg-4">
                        <Panel header="Dealer" style={{height: '100%'}}>
                        <p>
                                <img style={{height: "auto", maxWidth: "100%", marginLeft: "auto", marginRight:"auto", display: "block"}} src={"https://dkszktluuqk1z.cloudfront.net/" + this.state.img6} alt='pix'/>
                        </p>
                        </Panel>
                    </div>
                    <div className="p-col-12 p-md-6 p-lg-12">
                        <Panel header="Chart" style={{height: '100%'}}>
                            <Chart type="bar" data={chartdata} options={multiAxisOptions} />
                        </Panel>
                    </div>
                </div>
            );
        }
    }

export default withAuthenticator(App, true, [
    <SignIn/>
    ]);

// export default withAuthenticator(App, true);