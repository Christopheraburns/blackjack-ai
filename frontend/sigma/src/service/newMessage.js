import Amplify, { PubSub } from 'aws-amplify';
import { AWSIoTProvider } from '@aws-amplify/pubsub/lib/Providers';

// Amplify.addPluggable(new AWSIoTProvider({
//     aws_pubsub_region: 'us-east-1',
//     aws_pubsub_endpoint: 'wss://a24uoola4timn8-ats.iot.us-east-1.amazonaws.com/mqtt'
// }));

export default () => {
    let client = null;
    let sub1 = null;

    const clientWrapper = {};
    clientWrapper.connect = (sub1) => {
        client = PubSub();
        sub1 = client.subscribe('helloworld').subscribe({
            next: data => console.log('Message received', data),
            error: error => console.error(error),
            close: () => console.log('Done'),
        });
        return clientWrapper;
    }

    // You will no longer get messages for 'myTopicA'
    clientWrapper.sendMessage = () => {
            client.publish('helloworld', {
                msg: 'Hello to subscribers' }
            );
            return clientWrapper;
    }

    clientWrapper.unSub = (sub1) => {
        sub1.unsubscribe();
        return clientWrapper;
    }

    return clientWrapper;
};

// export class IoTService { 

//     async putEvent() {
//         return await PubSub.publish('helloworld', {
//             msg: 'Hello to subscribers' }
//         );
//     }

//     subscribe() {
//         return PubSub.subscribe('helloworld').subscribe({
//             next: data => console.log('Message received', data),
//             error: error => console.error(error),
//             close: () => console.log('Done'),
//         });
//     }
        
// }