// TemplateManagementComponent.js

Vue.component('template-management', {
    data() {
        return {
            existingTemplates: {},
            isNewTemplate: false,
            newTemplateName: '',
            templateName: '',
            templateDefinition:''
        };
    },
    watch: {
        templateDefinition(newTemplateDefinition) {
            this.$emit('template-definition-changed', newTemplateDefinition);
        },
    },
    methods: {
        async fetchTemplates() {
            try {
                const response = await fetch('http://localhost:5000/templates');
                this.existingTemplates = await response.json();
            } catch (error) {
                console.error('Error fetching templates:', error);
            }
        },
        async createTemplate() {
            try {
                let nameToUse = this.templateName;
                if (this.isNewTemplate) {
                    nameToUse = this.newTemplateName;
                }

                const response = await fetch('http://localhost:5000/template', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: nameToUse,
                        definition: this.templateDefinition,
                    }),
                });

                const data = await response.json();
                console.log(data.message);
                this.existingTemplates = data.templates;
                this.templateName = '';
                this.newTemplateName = ''; // Clear newTemplateName
                this.templateDefinition = '';
                this.isNewTemplate = false; // Reset isNewTemplate
            } catch (error) {
                console.error('Error creating template:', error);
            }
        },
        handleTemplateNameChange() {
            if (this.templateName === 'New...') {
                this.isNewTemplate = true;
                this.templateDefinition = '';
            } else if (this.existingTemplates[this.templateName]) {
                this.templateDefinition = this.existingTemplates[this.templateName];
                this.isNewTemplate = false;
            } else {
                this.templateDefinition = '';
                this.isNewTemplate = false;
            }
        },
    },
    mounted() {
        this.fetchTemplates();
    },
    template: `
        <div class="ml-4">
            <div class="form-group">
                <label for="template-name">Template Name</label>
                <div class="input-group">
                    <b-form-select class="m-2" :value="templateName" @input="templateName = $event" :options="[...Object.keys(existingTemplates), 'New...']" @change="handleTemplateNameChange"></b-form-select>
                    <input v-if="isNewTemplate" v-model="newTemplateName" class="form-control m-2" placeholder="Enter new template name">
                </div>
            </div>
            <div class="form-group">
                <label for="template-definition">Template Definition</label>
                <b-form-textarea id="template-definition" rows="5" v-model="templateDefinition"></b-form-textarea>
            </div>
            <div class="form-group">
                <b-button @click="createTemplate" variant="primary">Save Template</b-button>
            </div>
        </div>
    `,
});
