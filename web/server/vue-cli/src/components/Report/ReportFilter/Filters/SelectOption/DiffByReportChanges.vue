<template>
  <v-list-item-group lighten-4>
    <v-list-item class="my-1">
      <v-list-item-action class="ma-1 mr-5">
        <v-switch :input-value="value" @change="change" />
      </v-list-item-action>
      <v-list-item-content>
        <span>
          Diff by changes in report messages
          <tooltip-help-icon>
            TODO
          </tooltip-help-icon>
        </span>
      </v-list-item-content>
    </v-list-item>
  </v-list-item-group>
</template>

<script>
import TooltipHelpIcon from "@/components/TooltipHelpIcon.vue";

export default {
  name: "DiffByReportChanges",
  components: { TooltipHelpIcon },
  props: {
    value: { type: Boolean, default: false }
  },
  methods: {
    change(value) {
      this.$emit("input", value);
    }
  }
};
</script>
