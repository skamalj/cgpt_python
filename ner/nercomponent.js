// NERComponent.js

Vue.component('ner-component', {
    data() {
        return {
            nerText: '',
            temperatureNER: 0.5,
            nerResult: '',
        };
    },
    methods: {
        recognizeEntities() {
        }
    },
    template: `
        <b-tab title="NER">
            <b-row>
                <!-- NER Result -->
                <b-col cols="8">
                    <div class="form-group mt-2">
                        <label for="ner-text">Text for NER</label>
                        <input id="ner-text" type="text" class="form-control" v-model="nerText" placeholder="Enter text for NER" @keydown.enter="recognizeEntities">
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
                        <p>{{ nerResult }}</p>
                    </div>
                </b-col>

                <!-- Template Management Component -->
                <b-col cols="4">
                    <template-management class="ml-4"></template-management>
                </b-col>
            </b-row>
        </b-tab>
    `,
});
