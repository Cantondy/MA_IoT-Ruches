import { createRequire } from 'module';
const require = createRequire(import.meta.url);

const Influx = require('@influxdata/influxdb-client')

//This code writes data from IoT core rule via Lambda into InfluxDB 

export const handler = async (event,context,callback) => {

    var luminosityInputValue  = JSON.parse(event.luminosity);
    var humidityInputValue    = JSON.parse(event.humidity);
	var temperatureInputValue = JSON.parse(event.temperature);
    //Create clientID
    var sensorid = JSON.stringify(event.device_id);
    
    var result = writeToInfluxDB (luminosityInputValue, humidityInputValue, temperatureInputValue, sensorid);
    
    callback(null, result);

  };

function writeToInfluxDB(luminosityVar, humidityVar, temperatureVar, sensorVar)
{
    console.log("Executing Iflux insert");

    const client = new Influx.InfluxDB({
        database: process.env.INFLUXDB,
        username: process.env.INFLUXDBUSRNAME,
        password: process.env.INFLUXDBPWD,
        port: process.env.INFLUXDBPORT,
        hosts: [{ host: process.env.INFLUXDBHOST }],
        schema: [{
            measurement: 'ruche',
    
            fields:{
                humidity: Influx.FieldType.FLOAT, 
                luminosity: Influx.FieldType.FLOAT,
				temperature: Influx.FieldType.FLOAT,
            },
    
            tags: ['sensorID']
        }]
    });
    
    client.writePoints([{
        measurement: 'pressure', 
		fields: { 
			humidity: humidityVar, 
			luminosity: luminosityVar, 
			temperature: temperatureVar
		},
        tags: { sensorID: sensorVar}
    }]) 
    console.log("Finished executing");
}    