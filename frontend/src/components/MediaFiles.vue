<template>
  <div>
    <h2>Last processed files</h2>
    <DataTable :columns="columns" :rows="mediaRows" :perpage="5" />
  </div>
</template>
<script>
import DataTable from "./DataTable.vue";
import { parseMedia } from "../api";
export default {
  name: "MediaFiles",
  components: { DataTable },
  data() {
    return {
      props: {
        media: [],
      },
      columns: [
        { dataKey: "postId", name: "#", align: "right" },
        { dataKey: "mediaId", name: "Media ID", align: "left" },
        { dataKey: "status", name: "Status", align: "center" },
        { dataKey: "categories", name: "Categories", align: "left" },
      ],
    };
  },
  computed: {
    mediaRows() {
      return this.media.map((m) => parseMedia(m));
    },
  },
};
</script>
