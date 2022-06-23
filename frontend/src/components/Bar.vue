<template>
  <div class="greetings">
    <h1 class="green">{{ title }}</h1>
    <h3>{{ subtitle }}</h3>
    <h2 v-if="!loaded">Loading... {{ counter }}</h2>
    <Bar
      v-if="loaded"
      :chart-options="chartOptions"
      :chart-data="chartData"
      :chart-id="chartId"
      :dataset-id-key="datasetIdKey"
      :plugins="plugins"
      :css-classes="cssClasses"
      :styles="styles"
      :width="width"
      :height="height"
    />
    <h2>Last processed files</h2>
    <DataTable
      v-if="loaded"
      :columns="columns"
      :rows="mediaRows"
      :perpage="5"
    />
  </div>
</template>

<script>
import { Bar } from "vue-chartjs";
import DataTable from "./DataTable.vue";
import MediaFiles from "./MediaFiles.vue";
import { parseMedia } from "../api";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";
import { fetchApi } from "../api";
ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
);
const colors = ["#ef5350", "#d81b60", "#6a1b9a", "#673ab7", "#2196f3"];
export default {
  name: "BarChart",
  components: { Bar, DataTable, MediaFiles },
  props: {
    chartId: {
      type: String,
      default: "bar-chart",
    },
    datasetIdKey: {
      type: String,
      default: "label",
    },
    width: {
      type: Number,
      default: 400,
    },
    height: {
      type: Number,
      default: 400,
    },
    cssClasses: {
      default: "",
      type: String,
    },
    styles: {
      type: Object,
      default: () => {},
    },
    plugins: {
      type: Object,
      default: () => {},
    },
  },
  data() {
    return {
      loaded: false,
      error: null,
      title: "",
      subtitle: "",
      latest_media: [],
      chartData: {
        labels: ["Count"],
        datasets: [{ data: [40, 20, 12] }],
      },
      chartOptions: {
        responsive: true,
      },

      media: [],
      counter: 0,
      columns: [
        { dataKey: "postId", name: "#", align: "right" },
        { dataKey: "mediaIdLink", name: "Media ID", align: "left" },
        { dataKey: "status", name: "Status", align: "center" },
        { dataKey: "categories", name: "Categories", align: "left" },
      ],
    };
  },
  async mounted() {
    await this.fetchData();
    // setInterval(async () => {
    //   await this.fetchData();
    // }, 5000);
  },
  methods: {
    async fetchData() {
      this.counter++;
      console.log("fetching data");
      try {
        this.loaded = false;
        const {
          title,
          version,
          status,
          release,
          started_time,
          latest_media,
          subtitle,
        } = await fetchApi();
        console.log("fetchApi", {
          title,
          version,
          status,
          release,
          started_time,
          latest_media,
        });
        this.title = title;
        this.subtitle = subtitle;
        const data = [];
        let index = 0;
        for (const key in status) {
          data.push({
            label: key,
            data: [status[key]],
            backgroundColor: colors[index % colors.length],
          });
          index++;
        }

        this.chartData.datasets = data;
        this.media = latest_media;
        console.log("Latest media", latest_media);
        this.loaded = true;
      } catch (e) {
        this.error = e;
        console.error("Error fetching data", e);
      }
    },
  },
  computed: {
    getMedia() {
      return this.media;
    },

    mediaRows() {
      return this.media.map((m) => parseMedia(m));
    },
  },
};
</script>
<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  top: -10px;
}

h3 {
  font-size: 1.2rem;
}

.greetings h1,
.greetings h3 {
  text-align: center;
}

@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>
