// NERComponent.js

Vue.component('ner-component', {
    data() {
        return {
            nerFile: '',
            temperatureNER: 0.5,
            nerResult: '',
            templateDefinition: ''
        };
    },
    methods: {
        handleTemplateDefinitionChange(newTemplateDefinition) {
            this.templateDefinition = newTemplateDefinition;
        },
        async recognizeEntities() {
            try {
                const response = await fetch('http://localhost:5000/ner', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        filename: this.nerFile,
                        temperature: this.temperatureNER,
                        template_definition: this.templateDefinition
                    })
                });
    
                if (response.ok) {
                    const data = await response.json();
                    this.nerResult = data.summary;  // Assuming the response contains "ner_result" field
                } else {
                    this.nerResult = 'Error occurred during entity recognition.';
                }
            } catch (error) {
                console.error(error);
                this.nerResult = 'An error occurred.';
            }
        },
    },
    template: `
        <b-tab title="NER">
            <b-row>
                <!-- NER Result -->
                <b-col cols="8">
                    <div class="form-group mt-2">
                        <label for="ner-file">File for NER</label>
                        <input id="ner-file" type="text" class="form-control" v-model="nerFile" placeholder="Filename for NER" @keydown.enter="recognizeEntities">
                    </div>

                    <div class="form-group row mt-1">
                        <label for="ner-temperature" class="col-form-label col-md-4 mb-0" style="color: blue; font-family: Helvetica;">Set Temperature</label>
                        <div class="col-md-8">
                            <input id="ner-temperature" type="number" class="form-control" v-model="temperatureNER" placeholder="Enter Temperature" min="0" max="1" step="0.1">
                        </div>
                    </div>

                    <div class="form-group">
                        <b-button @click="recognizeEntities" variant="primary">Recognize Entities</b-button>
                    </div>

                    <div v-if="nerResult" class="form-group">
                        <h4>Named Entities:</h4>
                        <b-form-textarea rows="10" max-rows="15" v-model="nerResult"></b-form-textarea>
                    </div>
                </b-col>

                <!-- Template Management Component -->
                <b-col cols="4">
                    <template-management @template-definition-changed="handleTemplateDefinitionChange" class="ml-4"></template-management>
                </b-col>
            </b-row>
        </b-tab>
    `,
});
