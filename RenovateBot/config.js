module.exports = {
   platform: 'azure',
   endpoint: 'https://dev.azure.com/asml/',
   token: process.env.TOKEN,
   hostRules: [
     {
       hostType: 'npm',
       matchHost: 'pkgs.dev.azure.com',
       username: 'apikey',
       password: process.env.TOKEN,
     },
   ],
   autodiscover: true,
   autodiscoverFilter: ['ESDCloudOp/*'],
   rangeStrategy: 'pin'
 };